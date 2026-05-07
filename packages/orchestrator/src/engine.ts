import {
  type AgentId,
  type AgentResponseRecord,
  ALL_AGENT_IDS,
  agentLabel,
  createLogger,
} from '@agentboard/shared';
import { type AIProvider } from '@agentboard/ai';
import { type AgentRegistry } from '@agentboard/agents';
import {
  finishRun,
  recordAgentResponse,
  recordApiUsage,
  recordInternalAgentMessage,
  startRun,
  recentMessagesForChat,
  listTasks,
  listMemories,
} from '@agentboard/database';
import { formatMemoriesForPrompt, getMemoryStore, type RecalledMemory } from '@agentboard/memory';

const log = createLogger('orchestrator');

async function logUsage(
  run_id: string,
  responses: AgentResponseRecord[],
  cost_usd: number,
  model: string,
) {
  try {
    const tokens_in = responses.reduce((a, r) => a + r.tokens_in, 0);
    const tokens_out = responses.reduce((a, r) => a + r.tokens_out, 0);
    await recordApiUsage({ provider: 'anthropic', model, tokens_in, tokens_out, cost_usd, run_id });
  } catch {
    /* api_usage write must not break the orchestration */
  }
}

export interface OrchestrationContext {
  ai: AIProvider;
  registry: AgentRegistry;
  chat_id?: number;
  user_id?: number;
}

export interface OrchestrationResult {
  run_id: string;
  responses: AgentResponseRecord[];
  synthesis?: string;
  action_plan?: string;
  decision?: string;
  next_actions?: string;
  total_tokens: number;
  cost_usd: number;
  status: 'succeeded' | 'partial' | 'failed';
  partial_failures: AgentId[];
}

interface AgentCallResult {
  ok: boolean;
  record: AgentResponseRecord;
  err?: string;
}

async function callAgent(
  ctx: OrchestrationContext,
  args: {
    agent: AgentId;
    user_text: string;
    memory_block: string;
    extra_context?: string;
    round?: number;
    max_tokens?: number;
    temperature?: number;
  },
): Promise<AgentCallResult> {
  const def = ctx.registry.get(args.agent);
  const round = args.round ?? 1;
  const t0 = Date.now();
  const messages = [];
  if (args.memory_block) messages.push({ role: 'user' as const, content: args.memory_block });
  if (args.extra_context) messages.push({ role: 'user' as const, content: args.extra_context });
  messages.push({ role: 'user' as const, content: args.user_text });

  try {
    const res = await ctx.ai.generateText({
      system: def.system_prompt,
      messages,
      max_tokens: args.max_tokens ?? 700,
      temperature: args.temperature ?? 0.6,
    });
    return {
      ok: true,
      record: {
        agent_id: args.agent,
        round,
        content: res.text,
        tokens_in: res.tokens_in,
        tokens_out: res.tokens_out,
        latency_ms: Date.now() - t0,
      },
    };
  } catch (err) {
    log.error('agent call failed', { agent: args.agent, err: String(err) });
    if (def.failure_behavior === 'retry_once') {
      try {
        const res = await ctx.ai.generateText({
          system: def.system_prompt,
          messages,
          max_tokens: args.max_tokens ?? 700,
          temperature: args.temperature ?? 0.6,
        });
        return {
          ok: true,
          record: {
            agent_id: args.agent,
            round,
            content: res.text,
            tokens_in: res.tokens_in,
            tokens_out: res.tokens_out,
            latency_ms: Date.now() - t0,
          },
        };
      } catch (err2) {
        return {
          ok: false,
          err: String(err2),
          record: {
            agent_id: args.agent,
            round,
            content: `[${agentLabel(args.agent)} could not respond]`,
            tokens_in: 0,
            tokens_out: 0,
            latency_ms: Date.now() - t0,
          },
        };
      }
    }
    return {
      ok: false,
      err: String(err),
      record: {
        agent_id: args.agent,
        round,
        content: `[${agentLabel(args.agent)} skipped]`,
        tokens_in: 0,
        tokens_out: 0,
        latency_ms: Date.now() - t0,
      },
    };
  }
}

async function recallMemoryBlock(query: string): Promise<{
  ids: string[];
  block: string;
  recalled: RecalledMemory[];
}> {
  try {
    const recalled = await getMemoryStore().recall({ query, top_k: 6, min_similarity: 0.4 });
    return {
      ids: recalled.map((m) => m.id),
      block: formatMemoriesForPrompt(recalled),
      recalled,
    };
  } catch (err) {
    log.warn('memory recall failed', { err: String(err) });
    return { ids: [], block: '', recalled: [] };
  }
}

// ---------------- single ----------------

export async function runSingle(
  ctx: OrchestrationContext,
  args: { agent: AgentId; message: string },
): Promise<OrchestrationResult> {
  const { ids, block } = await recallMemoryBlock(args.message);
  const run = await startRun({
    chat_id: ctx.chat_id ?? null,
    user_id: ctx.user_id ?? null,
    mode: 'single',
    input_text: args.message,
    selected_agents: [args.agent],
  });
  const result = await callAgent(ctx, {
    agent: args.agent,
    user_text: args.message,
    memory_block: block,
  });
  const status: OrchestrationResult['status'] = result.ok ? 'succeeded' : 'failed';
  const cost = ctx.ai.estimateCost('default', result.record.tokens_in, result.record.tokens_out);
  await recordAgentResponse({ ...result.record, run_id: run.id });
  await finishRun(run.id, {
    status,
    total_tokens: result.record.tokens_in + result.record.tokens_out,
    cost_usd: cost,
    retrieved_memory_ids: ids,
    error: result.err ?? null,
  });
  await logUsage(run.id, [result.record], cost, 'default');
  return {
    run_id: run.id,
    responses: [result.record],
    total_tokens: result.record.tokens_in + result.record.tokens_out,
    cost_usd: cost,
    status,
    partial_failures: result.ok ? [] : [args.agent],
  };
}

// ---------------- board ----------------

export async function runBoard(
  ctx: OrchestrationContext,
  args: { message: string; agents?: AgentId[] },
): Promise<OrchestrationResult> {
  const agents = args.agents?.length ? args.agents : [...ALL_AGENT_IDS];
  const { ids, block } = await recallMemoryBlock(args.message);
  const run = await startRun({
    chat_id: ctx.chat_id ?? null,
    user_id: ctx.user_id ?? null,
    mode: 'board',
    input_text: args.message,
    selected_agents: agents,
  });

  // Step 1: fan out
  const fan = await Promise.all(
    agents.map((a) => callAgent(ctx, { agent: a, user_text: args.message, memory_block: block })),
  );
  const failures = fan.filter((r) => !r.ok).map((r) => r.record.agent_id);
  const responses: AgentResponseRecord[] = fan.map((r) => r.record);

  // Step 2: CEO synthesis (only if CEO is in the agent set; otherwise skip)
  const includeCeo = agents.includes('ceo');
  const ceoSynth = includeCeo
    ? await callAgent(ctx, {
        agent: 'ceo',
        user_text:
          'Synthesize the following agent responses into a single founder-level decision. ' +
          'End with a "Recommendation:" line.',
        memory_block: '',
        extra_context: buildSynthContext(args.message, fan),
        round: 2,
        max_tokens: 700,
        temperature: 0.4,
      })
    : null;

  // Step 3: Ops action plan
  const opsPlan = agents.includes('ops')
    ? await callAgent(ctx, {
        agent: 'ops',
        user_text:
          'Turn the synthesis below into a numbered action plan with 3–7 items. ' +
          'Each: action — owner — priority — deadline.',
        memory_block: '',
        extra_context: ceoSynth?.record.content
          ? `<synthesis>\n${ceoSynth.record.content}\n</synthesis>`
          : buildSynthContext(args.message, fan),
        round: 3,
        max_tokens: 600,
        temperature: 0.3,
      })
    : null;

  if (ceoSynth) responses.push(ceoSynth.record);
  if (opsPlan) responses.push(opsPlan.record);

  const status: OrchestrationResult['status'] =
    failures.length === 0 ? 'succeeded' : failures.length < agents.length ? 'partial' : 'failed';
  const total_tokens = responses.reduce((a, r) => a + r.tokens_in + r.tokens_out, 0);
  const cost_usd = responses.reduce(
    (a, r) => a + ctx.ai.estimateCost('default', r.tokens_in, r.tokens_out),
    0,
  );

  for (const r of responses) await recordAgentResponse({ ...r, run_id: run.id });
  await finishRun(run.id, {
    status,
    total_tokens,
    cost_usd,
    retrieved_memory_ids: ids,
    error: failures.length ? `partial: ${failures.join(',')}` : null,
  });
  await logUsage(run.id, responses, cost_usd, 'default');

  return {
    run_id: run.id,
    responses,
    synthesis: ceoSynth?.record.content,
    action_plan: opsPlan?.record.content,
    total_tokens,
    cost_usd,
    status,
    partial_failures: failures,
  };
}

function buildSynthContext(input: string, fan: AgentCallResult[]): string {
  const lines = [`<board_input>\n${input}\n</board_input>`, '<agent_responses>'];
  for (const r of fan) {
    if (!r.ok) continue;
    lines.push(`<${r.record.agent_id}>${r.record.content}</${r.record.agent_id}>`);
  }
  lines.push('</agent_responses>');
  return lines.join('\n');
}

// ---------------- debate ----------------

export async function runDebate(
  ctx: OrchestrationContext,
  args: { message: string },
): Promise<OrchestrationResult> {
  const agents = [...ALL_AGENT_IDS];
  const { ids, block } = await recallMemoryBlock(args.message);
  const run = await startRun({
    chat_id: ctx.chat_id ?? null,
    user_id: ctx.user_id ?? null,
    mode: 'debate',
    input_text: args.message,
    selected_agents: agents,
  });

  // Round 1: positions (in parallel)
  const round1 = await Promise.all(
    agents.map((a) =>
      callAgent(ctx, {
        agent: a,
        user_text:
          'Give your initial position on this. 5 sentences max. End with one bold "Position:" line.',
        memory_block: block,
        extra_context: `<topic>\n${args.message}\n</topic>`,
        round: 1,
        max_tokens: 350,
        temperature: 0.6,
      }),
    ),
  );

  const round1Block = `<round1_positions>\n${round1
    .filter((r) => r.ok)
    .map((r) => `<${r.record.agent_id}>${r.record.content}</${r.record.agent_id}>`)
    .join('\n')}\n</round1_positions>`;

  // Round 2: critiques (each critiques the others)
  const round2 = await Promise.all(
    agents.map((a) =>
      callAgent(ctx, {
        agent: a,
        user_text:
          'Critique the other agents\' positions. Be sharp but fair. Identify the strongest counter-argument to your own position. 6 sentences max.',
        memory_block: '',
        extra_context: round1Block,
        round: 2,
        max_tokens: 350,
        temperature: 0.5,
      }),
    ),
  );
  for (const r of round2) {
    if (r.ok) {
      await recordInternalAgentMessage({
        run_id: run.id,
        from_agent: r.record.agent_id,
        to_agent: null,
        round: 2,
        content: r.record.content,
      });
    }
  }

  const round2Block = `<round2_critiques>\n${round2
    .filter((r) => r.ok)
    .map((r) => `<${r.record.agent_id}>${r.record.content}</${r.record.agent_id}>`)
    .join('\n')}\n</round2_critiques>`;

  // Round 3: refined recommendations
  const round3 = await Promise.all(
    agents.map((a) =>
      callAgent(ctx, {
        agent: a,
        user_text:
          'Given the critiques, give your refined recommendation. 4 sentences max. End with "Recommendation:".',
        memory_block: '',
        extra_context: `${round1Block}\n${round2Block}`,
        round: 3,
        max_tokens: 300,
        temperature: 0.4,
      }),
    ),
  );

  // Final call from CEO
  const finalCall = await callAgent(ctx, {
    agent: 'ceo',
    user_text:
      'Based on the debate above, make the final call. State the chosen direction in one paragraph and a one-line "Decision:".',
    memory_block: '',
    extra_context:
      `<topic>${args.message}</topic>\n` +
      `<refined>\n${round3
        .filter((r) => r.ok)
        .map((r) => `<${r.record.agent_id}>${r.record.content}</${r.record.agent_id}>`)
        .join('\n')}\n</refined>`,
    round: 4,
    max_tokens: 350,
    temperature: 0.3,
  });

  // Action plan from Ops
  const actionPlan = await callAgent(ctx, {
    agent: 'ops',
    user_text:
      'Based on Atlas\'s decision, produce an execution plan: 3–6 numbered actions with owner, priority, deadline.',
    memory_block: '',
    extra_context: `<decision>${finalCall.record.content}</decision>`,
    round: 5,
    max_tokens: 400,
    temperature: 0.3,
  });

  const responses: AgentResponseRecord[] = [
    ...round1.map((r) => r.record),
    ...round2.map((r) => r.record),
    ...round3.map((r) => r.record),
    finalCall.record,
    actionPlan.record,
  ];
  const failures = [...round1, ...round2, ...round3, finalCall, actionPlan]
    .filter((r) => !r.ok)
    .map((r) => r.record.agent_id);

  const status: OrchestrationResult['status'] =
    failures.length === 0 ? 'succeeded' : failures.length < responses.length ? 'partial' : 'failed';
  const total_tokens = responses.reduce((a, r) => a + r.tokens_in + r.tokens_out, 0);
  const cost_usd = responses.reduce(
    (a, r) => a + ctx.ai.estimateCost('default', r.tokens_in, r.tokens_out),
    0,
  );

  for (const r of responses) await recordAgentResponse({ ...r, run_id: run.id });
  await finishRun(run.id, {
    status,
    total_tokens,
    cost_usd,
    retrieved_memory_ids: ids,
    error: failures.length ? `partial: ${failures.join(',')}` : null,
  });
  await logUsage(run.id, responses, cost_usd, 'default');

  return {
    run_id: run.id,
    responses,
    decision: finalCall.record.content,
    action_plan: actionPlan.record.content,
    total_tokens,
    cost_usd,
    status,
    partial_failures: failures,
  };
}

// ---------------- decision ----------------

export async function runDecision(
  ctx: OrchestrationContext,
  args: { message: string },
): Promise<OrchestrationResult> {
  const agents = [...ALL_AGENT_IDS];
  const { ids, block } = await recallMemoryBlock(args.message);
  const run = await startRun({
    chat_id: ctx.chat_id ?? null,
    user_id: ctx.user_id ?? null,
    mode: 'decision',
    input_text: args.message,
    selected_agents: agents,
  });

  const inputs = await Promise.all(
    agents.map((a) =>
      callAgent(ctx, {
        agent: a,
        user_text:
          'Give a quick input on this in ≤3 bullet points. No preamble. End with one "Vote:" line picking the option you favor.',
        memory_block: block,
        extra_context: `<topic>${args.message}</topic>`,
        round: 1,
        max_tokens: 250,
        temperature: 0.4,
      }),
    ),
  );

  const ctxBlock = `<inputs>\n${inputs
    .filter((r) => r.ok)
    .map((r) => `<${r.record.agent_id}>${r.record.content}</${r.record.agent_id}>`)
    .join('\n')}\n</inputs>`;

  const decision = await callAgent(ctx, {
    agent: 'ceo',
    user_text:
      'Make the call. State the choice in 2 sentences. End with one bold "Decision:" line.',
    memory_block: '',
    extra_context: ctxBlock,
    round: 2,
    max_tokens: 200,
    temperature: 0.2,
  });

  const next = await callAgent(ctx, {
    agent: 'ops',
    user_text: 'Give exactly the next 3 actions: action — owner — deadline.',
    memory_block: '',
    extra_context: `<decision>${decision.record.content}</decision>`,
    round: 3,
    max_tokens: 200,
    temperature: 0.2,
  });

  const responses = [...inputs.map((r) => r.record), decision.record, next.record];
  const failures = [...inputs, decision, next].filter((r) => !r.ok).map((r) => r.record.agent_id);

  const status: OrchestrationResult['status'] =
    failures.length === 0 ? 'succeeded' : failures.length < responses.length ? 'partial' : 'failed';
  const total_tokens = responses.reduce((a, r) => a + r.tokens_in + r.tokens_out, 0);
  const cost_usd = responses.reduce(
    (a, r) => a + ctx.ai.estimateCost('default', r.tokens_in, r.tokens_out),
    0,
  );

  for (const r of responses) await recordAgentResponse({ ...r, run_id: run.id });
  await finishRun(run.id, {
    status,
    total_tokens,
    cost_usd,
    retrieved_memory_ids: ids,
    error: failures.length ? `partial: ${failures.join(',')}` : null,
  });
  await logUsage(run.id, responses, cost_usd, 'default');

  return {
    run_id: run.id,
    responses,
    decision: decision.record.content,
    next_actions: next.record.content,
    total_tokens,
    cost_usd,
    status,
    partial_failures: failures,
  };
}

// ---------------- panic ----------------

export async function runPanic(
  ctx: OrchestrationContext,
  args: { problem: string },
): Promise<OrchestrationResult> {
  const { ids, block } = await recallMemoryBlock(args.problem);
  const run = await startRun({
    chat_id: ctx.chat_id ?? null,
    user_id: ctx.user_id ?? null,
    mode: 'panic',
    input_text: args.problem,
    selected_agents: ['cto', 'ceo', 'ops'],
  });

  const diag = await callAgent(ctx, {
    agent: 'cto',
    user_text:
      'EMERGENCY: diagnose technical risk and impact. State worst case, most-likely cause, and quickest mitigation. ≤5 sentences.',
    memory_block: block,
    extra_context: `<problem>${args.problem}</problem>`,
    round: 1,
    max_tokens: 350,
    temperature: 0.2,
  });
  const priority = await callAgent(ctx, {
    agent: 'ceo',
    user_text:
      'Set priority. Decide stop-the-world or contain. End with one "Priority:" line: P0/P1/P2.',
    memory_block: '',
    extra_context: `<diagnosis>${diag.record.content}</diagnosis>`,
    round: 2,
    max_tokens: 200,
    temperature: 0.2,
  });
  const triage = await callAgent(ctx, {
    agent: 'ops',
    user_text: 'Triage plan: who does what, in what order, in the next 2 hours.',
    memory_block: '',
    extra_context: `<priority>${priority.record.content}</priority>\n<diagnosis>${diag.record.content}</diagnosis>`,
    round: 3,
    max_tokens: 350,
    temperature: 0.2,
  });

  const responses = [diag.record, priority.record, triage.record];
  const failures = [diag, priority, triage].filter((r) => !r.ok).map((r) => r.record.agent_id);
  const status: OrchestrationResult['status'] =
    failures.length === 0 ? 'succeeded' : failures.length < 3 ? 'partial' : 'failed';

  const total_tokens = responses.reduce((a, r) => a + r.tokens_in + r.tokens_out, 0);
  const cost_usd = responses.reduce(
    (a, r) => a + ctx.ai.estimateCost('default', r.tokens_in, r.tokens_out),
    0,
  );
  for (const r of responses) await recordAgentResponse({ ...r, run_id: run.id });
  await finishRun(run.id, {
    status,
    total_tokens,
    cost_usd,
    retrieved_memory_ids: ids,
  });
  await logUsage(run.id, responses, cost_usd, 'default');

  return {
    run_id: run.id,
    responses,
    decision: priority.record.content,
    action_plan: triage.record.content,
    total_tokens,
    cost_usd,
    status,
    partial_failures: failures,
  };
}

// ---------------- brief ----------------

export async function runBrief(
  ctx: OrchestrationContext,
): Promise<OrchestrationResult> {
  const run = await startRun({
    chat_id: ctx.chat_id ?? null,
    user_id: ctx.user_id ?? null,
    mode: 'brief',
    input_text: 'Executive brief',
    selected_agents: ['ceo', 'ops'],
  });

  const recent = ctx.chat_id ? await recentMessagesForChat(ctx.chat_id, 24, 80) : [];
  const tasks = await listTasks({ status: ['open', 'in_progress', 'blocked'], limit: 30 });
  const memories = await listMemories(15);

  const ctxBlock = [
    `<recent_messages count="${recent.length}">`,
    recent
      .reverse()
      .map((m) => `[${m.role}] ${m.text.slice(0, 240)}`)
      .join('\n'),
    '</recent_messages>',
    `<open_tasks count="${tasks.length}">`,
    tasks.map((t) => `- ${t.priority}/${t.status}: ${t.title} (owner ${t.agent_id})`).join('\n'),
    '</open_tasks>',
    `<recent_memories count="${memories.length}">`,
    memories.map((m) => `- (${m.type}, imp ${m.importance_score.toFixed(2)}) ${m.summary ?? m.content.slice(0, 200)}`).join('\n'),
    '</recent_memories>',
  ].join('\n');

  const ceoSummary = await callAgent(ctx, {
    agent: 'ceo',
    user_text:
      'Produce an executive brief. Sections: Decisions made, Risks, Open priorities. ≤8 short bullets total.',
    memory_block: '',
    extra_context: ctxBlock,
    round: 1,
    max_tokens: 600,
    temperature: 0.3,
  });
  const opsActions = await callAgent(ctx, {
    agent: 'ops',
    user_text: 'List the next 5 highest-leverage actions for the next 24 hours.',
    memory_block: '',
    extra_context: ctxBlock,
    round: 2,
    max_tokens: 400,
    temperature: 0.3,
  });

  const responses = [ceoSummary.record, opsActions.record];
  const failures = [ceoSummary, opsActions].filter((r) => !r.ok).map((r) => r.record.agent_id);
  const status: OrchestrationResult['status'] =
    failures.length === 0 ? 'succeeded' : failures.length < 2 ? 'partial' : 'failed';
  const total_tokens = responses.reduce((a, r) => a + r.tokens_in + r.tokens_out, 0);
  const cost_usd = responses.reduce(
    (a, r) => a + ctx.ai.estimateCost('default', r.tokens_in, r.tokens_out),
    0,
  );
  for (const r of responses) await recordAgentResponse({ ...r, run_id: run.id });
  await finishRun(run.id, { status, total_tokens, cost_usd });
  await logUsage(run.id, responses, cost_usd, 'default');

  return {
    run_id: run.id,
    responses,
    synthesis: ceoSummary.record.content,
    action_plan: opsActions.record.content,
    total_tokens,
    cost_usd,
    status,
    partial_failures: failures,
  };
}
