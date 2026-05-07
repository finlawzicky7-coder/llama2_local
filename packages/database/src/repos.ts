import { getSql } from './client.js';
import type {
  AgentId,
  CreateMemory,
  CreateTask,
  Memory,
  OrchestrationMode,
  OrchestrationRun,
  Task,
  TaskStatus,
} from '@agentboard/shared';

// ---------------- agents ----------------

export interface AgentRow {
  id: AgentId;
  name: string;
  role: string;
  personality: string;
  system_prompt: string;
  decision_weight: number;
  status: 'active' | 'paused';
}

export async function listAgents(): Promise<AgentRow[]> {
  const sql = getSql();
  const rows = await sql<AgentRow[]>`
    select id, name, role, personality, system_prompt, decision_weight::float as decision_weight, status
    from public.agents order by id`;
  return rows;
}

// ---------------- telegram + messages ----------------

export async function upsertTelegramChat(args: {
  chat_id: number;
  title: string | null;
  type: string | null;
}) {
  const sql = getSql();
  await sql`
    insert into public.telegram_chats(chat_id, title, type)
    values (${args.chat_id}, ${args.title}, ${args.type})
    on conflict (chat_id) do update set title = excluded.title, type = excluded.type`;
}

export async function upsertTelegramUser(args: {
  user_id: number;
  username: string | null;
  first_name: string | null;
  is_admin: boolean;
}) {
  const sql = getSql();
  await sql`
    insert into public.telegram_users(user_id, username, first_name, is_admin)
    values (${args.user_id}, ${args.username}, ${args.first_name}, ${args.is_admin})
    on conflict (user_id) do update set
      username = excluded.username,
      first_name = excluded.first_name,
      is_admin = excluded.is_admin`;
}

export async function recordMessage(args: {
  chat_id: number;
  user_id: number | null;
  role: 'user' | 'assistant' | 'system';
  text: string;
  telegram_message_id?: number;
}) {
  const sql = getSql();
  const [row] = await sql<{ id: string }[]>`
    insert into public.messages (chat_id, user_id, role, text, telegram_message_id)
    values (${args.chat_id}, ${args.user_id}, ${args.role}, ${args.text}, ${args.telegram_message_id ?? null})
    returning id`;
  return row!.id;
}

export async function recentMessagesForChat(chat_id: number, hours = 24, limit = 200) {
  const sql = getSql();
  return sql<{ id: string; role: string; text: string; created_at: string; user_id: number | null }[]>`
    select id, role, text, created_at, user_id from public.messages
    where chat_id = ${chat_id} and created_at > now() - (${hours}::int || ' hours')::interval
    order by created_at desc limit ${limit}`;
}

// ---------------- orchestration runs ----------------

export async function startRun(args: {
  chat_id: number | null;
  user_id: number | null;
  mode: OrchestrationMode;
  input_text: string;
  selected_agents: AgentId[];
}): Promise<OrchestrationRun> {
  const sql = getSql();
  const [row] = await sql<OrchestrationRun[]>`
    insert into public.orchestration_runs (chat_id, user_id, mode, input_text, selected_agents)
    values (${args.chat_id}, ${args.user_id}, ${args.mode}, ${args.input_text}, ${args.selected_agents as unknown as string[]})
    returning *`;
  return row!;
}

export async function finishRun(
  id: string,
  args: {
    status: 'succeeded' | 'partial' | 'failed';
    total_tokens?: number;
    cost_usd?: number;
    error?: string | null;
    retrieved_memory_ids?: string[];
  },
) {
  const sql = getSql();
  await sql`
    update public.orchestration_runs set
      status = ${args.status},
      total_tokens = coalesce(${args.total_tokens ?? null}, total_tokens),
      cost_usd = coalesce(${args.cost_usd ?? null}, cost_usd),
      error = ${args.error ?? null},
      retrieved_memory_ids = coalesce(${args.retrieved_memory_ids as unknown as string[] ?? null}, retrieved_memory_ids),
      finished_at = now()
    where id = ${id}`;
}

export async function recordAgentResponse(args: {
  run_id: string;
  agent_id: AgentId;
  round: number;
  content: string;
  tokens_in: number;
  tokens_out: number;
  latency_ms: number;
}) {
  const sql = getSql();
  await sql`
    insert into public.agent_responses (run_id, agent_id, round, content, tokens_in, tokens_out, latency_ms)
    values (${args.run_id}, ${args.agent_id}, ${args.round}, ${args.content},
            ${args.tokens_in}, ${args.tokens_out}, ${args.latency_ms})`;
}

export async function recordInternalAgentMessage(args: {
  run_id: string;
  from_agent: AgentId;
  to_agent: AgentId | null;
  round: number;
  content: string;
}) {
  const sql = getSql();
  await sql`
    insert into public.internal_agent_messages (run_id, from_agent, to_agent, round, content)
    values (${args.run_id}, ${args.from_agent}, ${args.to_agent}, ${args.round}, ${args.content})`;
}

export async function recordApiUsage(args: {
  provider: string;
  model: string;
  tokens_in: number;
  tokens_out: number;
  cost_usd: number;
  run_id: string | null;
}) {
  const sql = getSql();
  await sql`
    insert into public.api_usage (provider, model, tokens_in, tokens_out, cost_usd, run_id)
    values (${args.provider}, ${args.model}, ${args.tokens_in}, ${args.tokens_out},
            ${args.cost_usd}, ${args.run_id})`;
}

// ---------------- tasks ----------------

export async function createTask(input: CreateTask): Promise<Task> {
  const sql = getSql();
  const [row] = await sql<Task[]>`
    insert into public.tasks (title, description, agent_id, priority, due_date, created_by, source_message_id)
    values (${input.title}, ${input.description ?? null}, ${input.agent_id}, ${input.priority},
            ${input.due_date ?? null}, ${input.created_by ?? null}, ${input.source_message_id ?? null})
    returning *`;
  return row!;
}

export async function listTasks(args: {
  status?: TaskStatus | TaskStatus[];
  agent?: AgentId;
  limit?: number;
} = {}): Promise<Task[]> {
  const sql = getSql();
  const statuses = args.status
    ? Array.isArray(args.status)
      ? args.status
      : [args.status]
    : ['open', 'in_progress', 'blocked'];
  return sql<Task[]>`
    select * from public.tasks
    where status = any(${statuses as unknown as string[]})
      ${args.agent ? sql`and agent_id = ${args.agent}` : sql``}
    order by case priority when 'urgent' then 0 when 'high' then 1 when 'medium' then 2 else 3 end,
             created_at desc
    limit ${args.limit ?? 100}`;
}

export async function getTask(id: string): Promise<Task | null> {
  const sql = getSql();
  const [row] = await sql<Task[]>`select * from public.tasks where id = ${id}`;
  return row ?? null;
}

export async function getTaskByShortId(shortId: string): Promise<Task | null> {
  const sql = getSql();
  const norm = shortId.replace(/[^0-9a-f]/gi, '').toLowerCase();
  const [row] = await sql<Task[]>`
    select * from public.tasks
    where replace(id::text, '-', '') like ${norm + '%'}
    order by created_at desc limit 1`;
  return row ?? null;
}

export async function updateTaskStatus(id: string, status: TaskStatus, changed_by: number | null) {
  const sql = getSql();
  const [old] = await sql<Task[]>`select * from public.tasks where id = ${id}`;
  if (!old) return null;
  const [row] = await sql<Task[]>`
    update public.tasks set status = ${status}, completed_at = ${status === 'done' ? new Date() : null}
    where id = ${id} returning *`;
  await sql`
    insert into public.task_updates (task_id, field, old_value, new_value, changed_by)
    values (${id}, 'status', ${old.status}, ${status}, ${changed_by})`;
  return row ?? null;
}

// ---------------- memory ----------------

export async function insertMemory(args: CreateMemory & { embedding: number[] }): Promise<Memory> {
  const sql = getSql();
  const vec = `[${args.embedding.join(',')}]`;
  const [row] = await sql<Memory[]>`
    insert into public.memories (type, content, summary, embedding, source, importance_score, expires_at, metadata)
    values (${args.type}, ${args.content}, ${args.summary ?? null}, ${vec}::vector,
            ${args.source ?? null}, ${args.importance_score},
            ${args.expires_at ?? null}, ${(args.metadata ?? {}) as Record<string, unknown>})
    returning id, type, content, summary, source, importance_score::float as importance_score,
              created_at, updated_at, expires_at, metadata`;
  return row!;
}

export async function listMemories(limit = 50): Promise<Memory[]> {
  const sql = getSql();
  return sql<Memory[]>`
    select id, type, content, summary, source, importance_score::float as importance_score,
           created_at, updated_at, expires_at, metadata
    from public.memories
    order by updated_at desc
    limit ${limit}`;
}

export async function searchMemories(args: {
  embedding: number[];
  top_k: number;
  min_similarity: number;
}): Promise<Array<Memory & { similarity: number }>> {
  const sql = getSql();
  const vec = `[${args.embedding.join(',')}]`;
  const rows = await sql<Array<Memory & { similarity: number }>>`
    select id, type, content, summary, source, importance_score::float as importance_score,
           created_at, updated_at, expires_at, metadata,
           1 - (embedding <=> ${vec}::vector) as similarity
    from public.memories
    where (expires_at is null or expires_at > now())
    order by embedding <=> ${vec}::vector
    limit ${args.top_k}`;
  return rows.filter((r) => r.similarity >= args.min_similarity);
}

export async function deleteMemory(id: string) {
  const sql = getSql();
  await sql`delete from public.memories where id = ${id}`;
}

// ---------------- logging ----------------

export async function logCommand(args: {
  chat_id: number | null;
  user_id: number | null;
  command: string;
  args: string | null;
  success: boolean;
}) {
  const sql = getSql();
  await sql`
    insert into public.command_history (chat_id, user_id, command, args, success)
    values (${args.chat_id}, ${args.user_id}, ${args.command}, ${args.args}, ${args.success})`;
}

export async function logSystem(args: {
  level: 'debug' | 'info' | 'warn' | 'error';
  source: string;
  message: string;
  metadata?: Record<string, unknown>;
}) {
  const sql = getSql();
  await sql`
    insert into public.system_logs (level, source, message, metadata)
    values (${args.level}, ${args.source}, ${args.message}, ${(args.metadata ?? {}) as Record<string, unknown>})`;
}

// ---------------- settings ----------------

export async function getSettings() {
  const sql = getSql();
  const [row] = await sql<
    { id: string; mode: string; default_model: string; rate_limit_per_min: number }[]
  >`select id, mode, default_model, rate_limit_per_min from public.app_settings where id = 'global'`;
  return row;
}

export async function setMode(mode: string) {
  const sql = getSql();
  await sql`update public.app_settings set mode = ${mode} where id = 'global'`;
}

// ---------------- dashboard helpers ----------------

export async function dashboardOverview() {
  const sql = getSql();
  const [open_tasks] = await sql<{ count: number }[]>`
    select count(*)::int as count from public.tasks where status in ('open','in_progress','blocked')`;
  const [memory_count] = await sql<{ count: number }[]>`
    select count(*)::int as count from public.memories`;
  const [recent_runs] = await sql<{ count: number }[]>`
    select count(*)::int as count from public.orchestration_runs where started_at > now() - interval '24 hours'`;
  const [tokens] = await sql<{ tokens: number; cost: number }[]>`
    select coalesce(sum(tokens_in + tokens_out),0)::int as tokens,
           coalesce(sum(cost_usd),0)::float as cost
    from public.api_usage where created_at > now() - interval '24 hours'`;
  return {
    open_tasks: open_tasks?.count ?? 0,
    memory_count: memory_count?.count ?? 0,
    recent_runs_24h: recent_runs?.count ?? 0,
    tokens_24h: tokens?.tokens ?? 0,
    cost_24h: tokens?.cost ?? 0,
  };
}

export async function recentRuns(limit = 25) {
  const sql = getSql();
  return sql<OrchestrationRun[]>`
    select * from public.orchestration_runs
    order by started_at desc limit ${limit}`;
}

export async function recentLogs(limit = 100) {
  const sql = getSql();
  return sql`
    select id, level, source, message, metadata, created_at from public.system_logs
    order by created_at desc limit ${limit}`;
}
