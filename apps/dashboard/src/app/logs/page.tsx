import { recentLogs } from '@agentboard/database';
import { Panel } from '@/components/sidebar';
import { safe } from '@/lib/safe';

export const dynamic = 'force-dynamic';

const LEVEL_COLOR: Record<string, string> = {
  info: 'text-ink',
  debug: 'text-muted',
  warn: 'text-warn',
  error: 'text-bad',
};

export default async function LogsPage() {
  const logs = await safe(() => recentLogs(200), [] as Array<{
    id: string;
    level: string;
    source: string;
    message: string;
    metadata: Record<string, unknown>;
    created_at: string;
  }>);
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold">Logs</h1>
        <p className="text-muted text-sm">System and queue activity, newest first.</p>
      </div>
      <Panel title={`Recent (${logs.length})`}>
        <ul className="font-mono text-xs divide-y divide-panelborder">
          {logs.map((l) => (
            <li key={l.id} className="py-2 flex items-start gap-3">
              <span className="text-muted whitespace-nowrap">
                {new Date(l.created_at).toLocaleTimeString()}
              </span>
              <span className={`uppercase w-12 ${LEVEL_COLOR[l.level] ?? ''}`}>{l.level}</span>
              <span className="text-accent w-32 truncate">{l.source}</span>
              <span className="text-ink flex-1 truncate">{l.message}</span>
            </li>
          ))}
          {logs.length === 0 ? (
            <li className="py-3 text-muted">No logs yet.</li>
          ) : null}
        </ul>
      </Panel>
    </div>
  );
}
