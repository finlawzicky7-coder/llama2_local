import {
  CreateMemoryInput,
  CreateTaskInput,
  RateLimiter,
  agentLabel,
  createLogger,
  formatAgentResponse,
  formatBoardSummary,
  formatDebateSummary,
  formatDecisionSummary,
  formatTaskCreated,
  formatTaskList,
  shortId,
  truncate,
  type AgentId,
} from '@agentboard/shared';
import { isAdmin, loadEnv } from '@agentboard/config';
import { getAIProvider } from '@agentboard/ai';
import { getAgentRegistry } from '@agentboard/agents';
import {
  createTask,
  getTaskByShortId,
  listTasks,
  logCommand,
  logSystem,
  recordMessage,
  setMode,
  updateTaskStatus,
  upsertTelegramChat,
  upsertTelegramUser,
} from '@agentboard/database';
import { getMemoryStore } from '@agentboard/memory';
import {
  parseCommand,
  routeMessage,
  runBoard,
  runBrief,
  runDebate,
  runDecision,
  runPanic,
  runSingle,
  type OrchestrationContext,
} from '@agentboard/orchestrator';

const log = createLogger('bot');
const env = loadEnv();
const rateLimiter = new RateLimiter(env.RATE_LIMIT_PER_MIN);

const SENSITIVE = new Set(['memory', 'task', 'done', 'mode', 'brief']);

export interface IncomingMessage {
  chat_id: number;
  chat_title: string | null;
  chat_type: string | null;
  user_id: number;
  username: string | null;
  first_name: string | null;
  text: string;
  message_id: number;
}

export interface BotReply {
  text: string;
  reply_to_message_id?: number;
}

async function ctx(msg: IncomingMessage): Promise<OrchestrationContext> {
  const registry = await getAgentRegistry();
  return {
    ai: getAIProvider(),
    registry,
    chat_id: msg.chat_id,
    user_id: msg.user_id,
  };
}

function adminGate(msg: IncomingMessage, command: string): BotReply | null {
  if (!SENSITIVE.has(command)) return null;
  if (isAdmin(msg.user_id)) return null;
  return {
    text: '_Sorry — that command is admin-only._',
    reply_to_message_id: msg.message_id,
  };
}

function rateLimitGate(msg: IncomingMessage): BotReply | null {
  if (rateLimiter.allow(msg.user_id)) return null;
  return {
    text: '_Slow down — rate limit hit. Try again in a moment._',
    reply_to_message_id: msg.message_id,
  };
}

async function recordIncoming(msg: IncomingMessage) {
  try {
    await upsertTelegramChat({
      chat_id: msg.chat_id,
      title: msg.chat_title,
      type: msg.chat_type,
    });
    await upsertTelegramUser({
      user_id: msg.user_id,
      username: msg.username,
      first_name: msg.first_name,
      is_admin: isAdmin(msg.user_id),
    });
    await recordMessage({
      chat_id: msg.chat_id,
      user_id: msg.user_id,
      role: 'user',
      text: msg.text,
      telegram_message_id: msg.message_id,
    });
  } catch (err) {
    log.warn('failed to record incoming', { err: String(err) });
  }
}

async function recordOutgoing(chat_id: number, text: string) {
  try {
    await recordMessage({ chat_id, user_id: null, role: 'assistant', text });
  } catch (err) {
    log.warn('failed to record outgoing', { err: String(err) });
  }
}

export async function handleMessage(msg: IncomingMessage): Promise<BotReply | null> {
  await recordIncoming(msg);

  const limited = rateLimitGate(msg);
  if (limited) return limited;

  const parsed = parseCommand(msg.text);
  if (parsed) {
    const blocked = adminGate(msg, parsed.kind);
    if (blocked) {
      await logCommand({
        chat_id: msg.chat_id,
        user_id: msg.user_id,
        command: parsed.kind,
        args: msg.text,
        success: false,
      });
      return blocked;
    }
    const reply = await dispatchCommand(parsed, msg);
    await logCommand({
      chat_id: msg.chat_id,
      user_id: msg.user_id,
      command: parsed.kind,
      args: msg.text.length > 500 ? msg.text.slice(0, 500) + '…' : msg.text,
      success: !!reply,
    });
    if (reply) await recordOutgoing(msg.chat_id, reply.text);
    return reply;
  }

  // Free-form: route via natural language
  const decision = await routeMessage(msg.text, { ai: tryGetAI() });
  log.info('nl route', { decision: decision.mode, agents: decision.agents });

  let reply: BotReply | null = null;
  switch (decision.mode) {
    case 'single':
      reply = await runSingleReply(msg, decision.agents[0] ?? 'ceo', msg.text);
      break;
    case 'board':
      reply = await runBoardReply(msg, msg.text, decision.agents);
      break;
    case 'debate':
      reply = await runDebateReply(msg, msg.text);
      break;
    case 'decision':
      reply = await runDecisionReply(msg, msg.text);
      break;
    case 'panic':
      reply = await runPanicReply(msg, msg.text);
      break;
    case 'memory':
      if (!isAdmin(msg.user_id)) {
        reply = { text: '_Storing memory is admin-only._', reply_to_message_id: msg.message_id };
      } else {
        reply = await runMemoryStore(msg, msg.text);
      }
      break;
    case 'task':
      reply = await runSingleReply(msg, 'ops', msg.text);
      break;
  }

  if (reply) await recordOutgoing(msg.chat_id, reply.text);
  return reply;
}

function tryGetAI() {
  try {
    return getAIProvider();
  } catch {
    return undefined;
  }
}

async function dispatchCommand(
  cmd: NonNullable<ReturnType<typeof parseCommand>>,
  msg: IncomingMessage,
): Promise<BotReply | null> {
  switch (cmd.kind) {
    case 'start':
      return { text: startMessage(), reply_to_message_id: msg.message_id };
    case 'help':
      return { text: helpMessage() };
    case 'agents':
      return { text: await agentsMessage() };
    case 'ask':
      return runSingleReply(msg, cmd.agent, cmd.message);
    case 'board':
      return runBoardReply(msg, cmd.message);
    case 'debate':
      return runDebateReply(msg, cmd.message);
    case 'decision':
      return runDecisionReply(msg, cmd.message);
    case 'panic':
      return runPanicReply(msg, cmd.problem);
    case 'task': {
      const parsed = CreateTaskInput.safeParse({
        agent_id: cmd.agent,
        priority: cmd.priority,
        title: cmd.title,
        created_by: msg.user_id,
        source_message_id: String(msg.message_id),
      });
      if (!parsed.success) {
        return { text: `_Invalid task: ${parsed.error.issues[0]?.message ?? 'bad input'}_` };
      }
      const task = await createTask(parsed.data);
      return { text: formatTaskCreated(task, env.DASHBOARD_URL) };
    }
    case 'tasks': {
      const tasks = await listTasks({ status: ['open', 'in_progress', 'blocked'] });
      return { text: `*Open tasks (${tasks.length})*\n\n${formatTaskList(tasks)}` };
    }
    case 'done': {
      const t = (await getTaskByShortId(cmd.id)) ?? null;
      if (!t) return { text: `_Task #${cmd.id} not found._` };
      const updated = await updateTaskStatus(t.id, 'done', msg.user_id);
      if (!updated) return { text: `_Could not update task #${cmd.id}._` };
      return { text: `*Done* #${shortId(updated.id)} — ${updated.title}` };
    }
    case 'memory':
      return runMemoryStore(msg, cmd.note);
    case 'recall': {
      const hits = await getMemoryStore().recall({ query: cmd.query, top_k: 6, min_similarity: 0.4 });
      if (!hits.length) return { text: '_No matching memory._' };
      const lines = hits.map(
        (m, i) =>
          `*${i + 1}.* (${m.type}, sim ${m.similarity.toFixed(2)}) ${truncate(
            m.summary ?? m.content,
            240,
          )}`,
      );
      return { text: `*Recall:*\n${lines.join('\n')}` };
    }
    case 'brief': {
      const r = await runBrief(await ctx(msg));
      const text = [
        '*Executive Brief*',
        '',
        `*Atlas:*\n${r.synthesis ?? ''}`,
        '',
        `*Ledger — next actions:*\n${r.action_plan ?? ''}`,
      ].join('\n');
      return { text };
    }
    case 'mode': {
      const allowed = ['brainstorm', 'execute', 'aggressive', 'research', 'investor', 'builder'];
      if (!allowed.includes(cmd.mode)) {
        return { text: `_Unknown mode. Choose one of: ${allowed.join(', ')}_` };
      }
      await setMode(cmd.mode);
      return { text: `*Mode set:* ${cmd.mode}` };
    }
    case 'invalid':
      return { text: `_${cmd.reason}_` };
    case 'unknown':
      return { text: `_Unknown command. Try /help._` };
  }
}

async function runSingleReply(
  msg: IncomingMessage,
  agent: AgentId,
  message: string,
): Promise<BotReply> {
  try {
    const r = await runSingle(await ctx(msg), { agent, message });
    const single = r.responses[0];
    if (!single) return { text: '_No response._' };
    return { text: formatAgentResponse(agent, single.content) };
  } catch (err) {
    await logSystem({
      level: 'error',
      source: 'bot',
      message: 'runSingle failed',
      metadata: { err: String(err) },
    });
    return { text: `_${agentLabel(agent)} could not respond. Try again in a moment._` };
  }
}

async function runBoardReply(
  msg: IncomingMessage,
  message: string,
  agents?: AgentId[],
): Promise<BotReply> {
  try {
    const r = await runBoard(await ctx(msg), { message, agents });
    return {
      text: formatBoardSummary({
        input: message,
        responses: r.responses,
        synthesis: r.synthesis ?? '',
        action_plan: r.action_plan ?? '',
      }),
    };
  } catch (err) {
    await logSystem({
      level: 'error',
      source: 'bot',
      message: 'runBoard failed',
      metadata: { err: String(err) },
    });
    return { text: '_Board run failed. Check logs._' };
  }
}

async function runDebateReply(msg: IncomingMessage, message: string): Promise<BotReply> {
  try {
    const r = await runDebate(await ctx(msg), { message });
    return {
      text: formatDebateSummary({
        input: message,
        rounds: r.responses,
        final_call: r.decision ?? '',
        action_plan: r.action_plan ?? '',
      }),
    };
  } catch (err) {
    await logSystem({
      level: 'error',
      source: 'bot',
      message: 'runDebate failed',
      metadata: { err: String(err) },
    });
    return { text: '_Debate run failed. Check logs._' };
  }
}

async function runDecisionReply(msg: IncomingMessage, message: string): Promise<BotReply> {
  try {
    const r = await runDecision(await ctx(msg), { message });
    const inputs = r.responses.filter((x) => x.round === 1);
    return {
      text: formatDecisionSummary({
        input: message,
        inputs,
        decision: r.decision ?? '',
        next_actions: r.next_actions ?? '',
      }),
    };
  } catch (err) {
    await logSystem({
      level: 'error',
      source: 'bot',
      message: 'runDecision failed',
      metadata: { err: String(err) },
    });
    return { text: '_Decision run failed. Check logs._' };
  }
}

async function runPanicReply(msg: IncomingMessage, problem: string): Promise<BotReply> {
  try {
    const r = await runPanic(await ctx(msg), { problem });
    const cto = r.responses.find((x) => x.agent_id === 'cto');
    const ceo = r.responses.find((x) => x.agent_id === 'ceo');
    const ops = r.responses.find((x) => x.agent_id === 'ops');
    const text = [
      `*PANIC — ${truncate(problem, 200)}*`,
      '',
      cto ? formatAgentResponse('cto', cto.content) : '',
      '',
      ceo ? formatAgentResponse('ceo', ceo.content) : '',
      '',
      ops ? formatAgentResponse('ops', ops.content) : '',
    ]
      .filter(Boolean)
      .join('\n');
    return { text };
  } catch (err) {
    await logSystem({
      level: 'error',
      source: 'bot',
      message: 'runPanic failed',
      metadata: { err: String(err) },
    });
    return { text: '_Panic run failed. Check logs._' };
  }
}

async function runMemoryStore(msg: IncomingMessage, note: string): Promise<BotReply> {
  const parsed = CreateMemoryInput.safeParse({
    type: 'business_context',
    content: note,
    summary: truncate(note, 200),
    importance_score: 0.7,
    source: `telegram:${msg.user_id}`,
  });
  if (!parsed.success) {
    return { text: `_Invalid memory: ${parsed.error.issues[0]?.message ?? 'bad input'}_` };
  }
  try {
    const { memory, deduped } = await getMemoryStore().store(parsed.data);
    return {
      text: deduped
        ? `*Memory deduped* — already saved as #${shortId(memory.id)}`
        : `*Memory saved* — #${shortId(memory.id)}`,
    };
  } catch (err) {
    await logSystem({
      level: 'error',
      source: 'bot',
      message: 'memory store failed',
      metadata: { err: String(err) },
    });
    return { text: '_Could not store memory (embedding provider missing?)._' };
  }
}

// ------- canned replies -------

function startMessage() {
  return [
    '*AgentBoard OS — online.*',
    '',
    'Five agents are watching this chat: *Atlas* (CEO), *Forge* (CTO), *Viper* (Sales), *Nova* (Marketing), *Ledger* (Ops).',
    '',
    'Type `/help` to see commands, `/agents` to see who is on the board, or just write naturally — e.g. _"Atlas, what should I do this week?"_.',
  ].join('\n');
}

function helpMessage() {
  return [
    '*AgentBoard OS — commands*',
    '',
    '/agents — list agents',
    '/ask <agent> <msg> — ask one agent',
    '/board <msg> — full boardroom',
    '/debate <msg> — 3-round debate',
    '/decision <msg> — quick call',
    '/panic <problem> — emergency triage',
    '/brief — executive summary (admin)',
    '/task <agent> <priority> <task> — create task (admin)',
    '/tasks — list open tasks',
    '/done <task_id> — mark task complete (admin)',
    '/memory <note> — store memory (admin)',
    '/recall <query> — search memory',
    '/mode <mode> — switch operating mode (admin)',
    '',
    'Or just talk naturally — e.g. _"Forge, design the scraper"_.',
  ].join('\n');
}

async function agentsMessage(): Promise<string> {
  const reg = await getAgentRegistry();
  return [
    '*Board:*',
    ...reg.list().map(
      (a) =>
        `• *${a.name}* (${a.role}) — _${a.personality.split('.')[0]}_`,
    ),
  ].join('\n');
}
