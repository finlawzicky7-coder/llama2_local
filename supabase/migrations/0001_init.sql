-- AgentBoard OS — initial schema
-- Idempotent: safe to run multiple times in dev.

create extension if not exists "pgcrypto";
create extension if not exists "vector";

-- ---------- updated_at trigger helper ----------
create or replace function set_updated_at() returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

-- ---------- agents ----------
create table if not exists public.agents (
  id text primary key,
  name text not null,
  role text not null,
  personality text not null,
  system_prompt text not null,
  decision_weight numeric not null default 0.2,
  status text not null default 'active' check (status in ('active','paused')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
drop trigger if exists trg_agents_updated on public.agents;
create trigger trg_agents_updated before update on public.agents
  for each row execute procedure set_updated_at();

-- ---------- telegram ----------
create table if not exists public.telegram_chats (
  chat_id bigint primary key,
  title text,
  type text,
  created_at timestamptz not null default now()
);

create table if not exists public.telegram_users (
  user_id bigint primary key,
  username text,
  first_name text,
  is_admin boolean not null default false,
  created_at timestamptz not null default now()
);

-- ---------- conversations ----------
create table if not exists public.conversations (
  id uuid primary key default gen_random_uuid(),
  chat_id bigint references public.telegram_chats(chat_id) on delete cascade,
  title text,
  mode text,
  last_active_at timestamptz not null default now()
);
create index if not exists idx_conv_chat on public.conversations(chat_id, last_active_at desc);

create table if not exists public.messages (
  id uuid primary key default gen_random_uuid(),
  chat_id bigint,
  user_id bigint,
  role text not null check (role in ('user','assistant','system')),
  text text not null,
  telegram_message_id bigint,
  created_at timestamptz not null default now()
);
create index if not exists idx_msg_chat_created on public.messages(chat_id, created_at desc);

-- ---------- orchestration ----------
create table if not exists public.orchestration_runs (
  id uuid primary key default gen_random_uuid(),
  chat_id bigint,
  user_id bigint,
  mode text not null,
  input_text text not null,
  selected_agents text[] not null default '{}',
  retrieved_memory_ids uuid[] not null default '{}',
  status text not null default 'running' check (status in ('running','succeeded','partial','failed')),
  total_tokens integer not null default 0,
  cost_usd numeric not null default 0,
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  error text
);
create index if not exists idx_runs_chat_started on public.orchestration_runs(chat_id, started_at desc);

create table if not exists public.agent_responses (
  id uuid primary key default gen_random_uuid(),
  run_id uuid references public.orchestration_runs(id) on delete cascade,
  agent_id text not null,
  round integer not null default 1,
  content text not null,
  tokens_in integer not null default 0,
  tokens_out integer not null default 0,
  latency_ms integer not null default 0,
  created_at timestamptz not null default now()
);
create index if not exists idx_resp_run on public.agent_responses(run_id, round);

create table if not exists public.internal_agent_messages (
  id uuid primary key default gen_random_uuid(),
  run_id uuid references public.orchestration_runs(id) on delete cascade,
  from_agent text not null,
  to_agent text,
  round integer not null,
  content text not null,
  created_at timestamptz not null default now()
);
create index if not exists idx_iam_run on public.internal_agent_messages(run_id, round);

-- ---------- tasks ----------
create table if not exists public.tasks (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  description text,
  agent_id text not null,
  status text not null default 'open' check (status in ('open','in_progress','blocked','done','canceled')),
  priority text not null default 'medium' check (priority in ('low','medium','high','urgent')),
  due_date timestamptz,
  created_by bigint,
  source_message_id text,
  dependencies uuid[] not null default '{}',
  progress_notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  completed_at timestamptz
);
create index if not exists idx_tasks_status_agent on public.tasks(status, agent_id);
create index if not exists idx_tasks_priority on public.tasks(priority, status);
drop trigger if exists trg_tasks_updated on public.tasks;
create trigger trg_tasks_updated before update on public.tasks
  for each row execute procedure set_updated_at();

create table if not exists public.task_updates (
  id uuid primary key default gen_random_uuid(),
  task_id uuid references public.tasks(id) on delete cascade,
  field text not null,
  old_value text,
  new_value text,
  changed_by bigint,
  created_at timestamptz not null default now()
);
create index if not exists idx_task_updates on public.task_updates(task_id, created_at desc);

-- ---------- memory ----------
create table if not exists public.memories (
  id uuid primary key default gen_random_uuid(),
  type text not null default 'system_note',
  content text not null,
  summary text,
  embedding vector(1536),
  source text,
  importance_score numeric not null default 0.5,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  expires_at timestamptz,
  metadata jsonb not null default '{}'::jsonb
);
create index if not exists idx_memories_type_imp on public.memories(type, importance_score desc);
create index if not exists idx_memories_embedding
  on public.memories using ivfflat (embedding vector_cosine_ops) with (lists = 100);
drop trigger if exists trg_memories_updated on public.memories;
create trigger trg_memories_updated before update on public.memories
  for each row execute procedure set_updated_at();

-- ---------- audit ----------
create table if not exists public.command_history (
  id uuid primary key default gen_random_uuid(),
  chat_id bigint,
  user_id bigint,
  command text not null,
  args text,
  success boolean not null default true,
  created_at timestamptz not null default now()
);
create index if not exists idx_cmd_user on public.command_history(user_id, created_at desc);

create table if not exists public.system_logs (
  id uuid primary key default gen_random_uuid(),
  level text not null default 'info',
  source text not null,
  message text not null,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
create index if not exists idx_logs_created on public.system_logs(created_at desc);
create index if not exists idx_logs_level on public.system_logs(level, created_at desc);

create table if not exists public.api_usage (
  id uuid primary key default gen_random_uuid(),
  provider text not null,
  model text not null,
  tokens_in integer not null default 0,
  tokens_out integer not null default 0,
  cost_usd numeric not null default 0,
  run_id uuid,
  created_at timestamptz not null default now()
);
create index if not exists idx_usage_provider on public.api_usage(provider, created_at desc);

create table if not exists public.user_permissions (
  user_id bigint primary key,
  role text not null default 'admin' check (role in ('admin','viewer')),
  created_at timestamptz not null default now()
);

create table if not exists public.app_settings (
  id text primary key default 'global',
  mode text not null default 'execute',
  default_model text not null default 'claude-sonnet-4-6',
  rate_limit_per_min integer not null default 20,
  updated_at timestamptz not null default now()
);
drop trigger if exists trg_app_settings_updated on public.app_settings;
create trigger trg_app_settings_updated before update on public.app_settings
  for each row execute procedure set_updated_at();

insert into public.app_settings(id) values ('global') on conflict do nothing;
