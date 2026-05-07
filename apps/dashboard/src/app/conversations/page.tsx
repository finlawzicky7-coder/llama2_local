import { recentRuns } from '@agentboard/database';
import { Panel } from '@/components/sidebar';
import { safe } from '@/lib/safe';

export const dynamic = 'force-dynamic';

export default async function ConversationsPage() {
  const runs = await safe(() => recentRuns(50), []);
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold">Conversations</h1>
        <p className="text-muted text-sm">Orchestration runs, newest first.</p>
      </div>
      <Panel title={`Runs (${runs.length})`}>
        <ul className="divide-y divide-panelborder">
          {runs.map((r) => (
            <li key={r.id} className="py-3">
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <div className="text-xs font-mono text-accent">{r.mode}</div>
                  <div className="text-sm truncate">{r.input_text}</div>
                  <div className="text-xs text-muted mt-1">
                    {r.selected_agents.join(', ')} • {r.status} • {r.total_tokens} tokens • $
                    {Number(r.cost_usd).toFixed(4)}
                  </div>
                </div>
                <div className="text-xs text-muted whitespace-nowrap">
                  {new Date(r.started_at).toLocaleString()}
                </div>
              </div>
              {r.error ? (
                <div className="text-xs text-bad mt-1">error: {r.error}</div>
              ) : null}
            </li>
          ))}
          {runs.length === 0 ? <li className="py-3 text-muted text-sm">No runs yet.</li> : null}
        </ul>
      </Panel>
    </div>
  );
}
