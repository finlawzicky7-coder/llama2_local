import { listMemories } from '@agentboard/database';
import { Panel } from '@/components/sidebar';
import { safe } from '@/lib/safe';

export const dynamic = 'force-dynamic';

export default async function MemoryPage() {
  const memories = await safe(() => listMemories(100), []);
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold">Memory</h1>
        <p className="text-muted text-sm">
          pgvector-backed long-term memory. Use the Telegram bot's <code>/memory</code> and{' '}
          <code>/recall</code> to add and search.
        </p>
      </div>
      <Panel title={`Recent memories (${memories.length})`}>
        <ul className="divide-y divide-panelborder">
          {memories.map((m) => (
            <li key={m.id} className="py-3">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-mono text-accent">{m.type}</span>
                <span className="text-xs text-muted">
                  imp {Number(m.importance_score).toFixed(2)}
                </span>
              </div>
              <div className="text-sm">{m.summary ?? m.content.slice(0, 220)}</div>
              <div className="text-xs text-muted mt-1">
                {new Date(m.created_at).toLocaleString()}
                {m.source ? ` • ${m.source}` : ''}
              </div>
            </li>
          ))}
          {memories.length === 0 ? (
            <li className="py-3 text-muted text-sm">No memories yet.</li>
          ) : null}
        </ul>
      </Panel>
    </div>
  );
}
