import { dashboardOverview, recentRuns } from '@agentboard/database';
import { Panel, StatCard } from '@/components/sidebar';
import { safe } from '@/lib/safe';

export const dynamic = 'force-dynamic';

export default async function OverviewPage() {
  const overview = await safe(() => dashboardOverview(), {
    open_tasks: 0,
    memory_count: 0,
    recent_runs_24h: 0,
    tokens_24h: 0,
    cost_24h: 0,
  });
  const runs = await safe(() => recentRuns(8), []);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold">Overview</h1>
        <p className="text-muted text-sm">Last 24h activity across the board.</p>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <StatCard label="Open tasks" value={overview.open_tasks} />
        <StatCard label="Memory count" value={overview.memory_count} />
        <StatCard label="Runs (24h)" value={overview.recent_runs_24h} />
        <StatCard label="Tokens (24h)" value={overview.tokens_24h.toLocaleString()} />
        <StatCard
          label="Cost (24h)"
          value={`$${overview.cost_24h.toFixed(3)}`}
          hint="estimated"
        />
      </div>
      <Panel title="Recent orchestration runs">
        {!runs.length ? (
          <p className="text-muted text-sm">No runs yet.</p>
        ) : (
          <ul className="divide-y divide-panelborder">
            {runs.map((r) => (
              <li key={r.id} className="py-3 flex items-start justify-between gap-4">
                <div>
                  <div className="text-sm font-mono text-accent">{r.mode}</div>
                  <div className="text-sm text-ink line-clamp-1">{r.input_text}</div>
                  <div className="text-xs text-muted">
                    {r.selected_agents.join(', ')} • {r.status} • {r.total_tokens} tokens
                  </div>
                </div>
                <div className="text-xs text-muted whitespace-nowrap">
                  {new Date(r.started_at).toLocaleString()}
                </div>
              </li>
            ))}
          </ul>
        )}
      </Panel>
    </div>
  );
}
