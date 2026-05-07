-- Row-level security. Service role bypasses; authenticated dashboard
-- users can only read if they exist in user_permissions with role='admin'.

alter table public.agents                 enable row level security;
alter table public.telegram_chats         enable row level security;
alter table public.telegram_users         enable row level security;
alter table public.conversations          enable row level security;
alter table public.messages               enable row level security;
alter table public.orchestration_runs     enable row level security;
alter table public.agent_responses        enable row level security;
alter table public.internal_agent_messages enable row level security;
alter table public.tasks                  enable row level security;
alter table public.task_updates           enable row level security;
alter table public.memories               enable row level security;
alter table public.command_history        enable row level security;
alter table public.system_logs            enable row level security;
alter table public.api_usage              enable row level security;
alter table public.user_permissions       enable row level security;
alter table public.app_settings           enable row level security;

-- Helper: is the requester an admin (matched by Telegram user_id stored in jwt claim 'tg_id')?
create or replace function public.is_admin_jwt() returns boolean language sql stable as $$
  select exists (
    select 1
    from public.user_permissions
    where role = 'admin'
      and user_id = nullif(current_setting('request.jwt.claims', true)::json ->> 'tg_id','')::bigint
  );
$$;

do $$ declare t text;
begin
  for t in
    select unnest(array[
      'agents','telegram_chats','telegram_users','conversations','messages',
      'orchestration_runs','agent_responses','internal_agent_messages',
      'tasks','task_updates','memories','command_history','system_logs',
      'api_usage','user_permissions','app_settings'
    ])
  loop
    execute format('drop policy if exists %I on public.%I;', t || '_admin_select', t);
    execute format(
      'create policy %I on public.%I for select to authenticated using (public.is_admin_jwt());',
      t || '_admin_select', t
    );
  end loop;
end $$;
