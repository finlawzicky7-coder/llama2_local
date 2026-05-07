import { getSettings, listAgents } from '@agentboard/database';
import { loadEnv } from '@agentboard/config';
import { Panel } from '@/components/sidebar';
import { safe } from '@/lib/safe';

export const dynamic = 'force-dynamic';

function check(ok: boolean) {
  return ok ? <span className="text-good">✓ ok</span> : <span className="text-warn">unset</span>;
}

export default async function SettingsPage() {
  let env: ReturnType<typeof loadEnv> | null = null;
  try {
    env = loadEnv();
  } catch {
    /* missing keys, render unset */
  }
  const settings = await safe(() => getSettings(), undefined);
  const agents = await safe(() => listAgents(), []);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold">Settings</h1>
        <p className="text-muted text-sm">Read-only summary of configuration.</p>
      </div>
      <Panel title="Environment">
        <ul className="text-sm space-y-1">
          <li>ANTHROPIC_API_KEY {check(!!env?.ANTHROPIC_API_KEY)}</li>
          <li>TELEGRAM_BOT_TOKEN {check(!!env?.TELEGRAM_BOT_TOKEN)}</li>
          <li>TELEGRAM_WEBHOOK_SECRET {check(!!env?.TELEGRAM_WEBHOOK_SECRET)}</li>
          <li>
            TELEGRAM_ADMIN_USER_IDS{' '}
            {check(!!env && env.TELEGRAM_ADMIN_USER_IDS.length > 0)}
            {env && env.TELEGRAM_ADMIN_USER_IDS.length > 0 ? (
              <span className="text-muted ml-2">
                ({env.TELEGRAM_ADMIN_USER_IDS.length} admin{env.TELEGRAM_ADMIN_USER_IDS.length > 1 ? 's' : ''})
              </span>
            ) : null}
          </li>
          <li>DATABASE_URL {check(!!env?.DATABASE_URL)}</li>
          <li>REDIS_URL {check(!!env?.REDIS_URL)}</li>
          <li>EMBEDDING_PROVIDER: <span className="font-mono text-accent">{env?.EMBEDDING_PROVIDER ?? 'unset'}</span></li>
          <li>DEFAULT_MODEL: <span className="font-mono text-accent">{env?.DEFAULT_MODEL ?? 'unset'}</span></li>
        </ul>
      </Panel>
      <Panel title="App settings">
        {settings ? (
          <ul className="text-sm space-y-1">
            <li>mode: <span className="font-mono text-accent">{settings.mode}</span></li>
            <li>default_model: <span className="font-mono text-accent">{settings.default_model}</span></li>
            <li>rate_limit_per_min: <span className="font-mono text-accent">{settings.rate_limit_per_min}</span></li>
          </ul>
        ) : (
          <p className="text-muted text-sm">No settings row (DB unreachable).</p>
        )}
      </Panel>
      <Panel title="Agent prompts">
        <ul className="space-y-3">
          {agents.map((a) => (
            <li key={a.id} className="border border-panelborder rounded p-3">
              <div className="text-sm font-semibold">
                {a.name} <span className="text-muted">({a.role})</span>
              </div>
              <pre className="text-xs text-muted whitespace-pre-wrap mt-2">{a.system_prompt}</pre>
            </li>
          ))}
          {agents.length === 0 ? (
            <li className="text-muted text-sm">
              Run <code>pnpm db:seed</code> to populate the 5 agents.
            </li>
          ) : null}
        </ul>
      </Panel>
    </div>
  );
}
