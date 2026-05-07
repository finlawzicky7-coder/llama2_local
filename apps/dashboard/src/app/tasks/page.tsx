import { listTasks } from '@agentboard/database';
import { Panel } from '@/components/sidebar';
import { shortId, type TaskStatus } from '@agentboard/shared';
import { safe } from '@/lib/safe';

export const dynamic = 'force-dynamic';

const COLUMNS: { key: TaskStatus; label: string }[] = [
  { key: 'open', label: 'Open' },
  { key: 'in_progress', label: 'In progress' },
  { key: 'blocked', label: 'Blocked' },
  { key: 'done', label: 'Done' },
];

const PRIORITY_COLOR: Record<string, string> = {
  low: 'text-muted',
  medium: 'text-ink',
  high: 'text-warn',
  urgent: 'text-bad',
};

export default async function TasksPage() {
  const tasks = await safe(
    () => listTasks({ status: ['open', 'in_progress', 'blocked', 'done'], limit: 200 }),
    [],
  );
  const byStatus = new Map<TaskStatus, typeof tasks>();
  for (const c of COLUMNS) byStatus.set(c.key, []);
  for (const t of tasks) byStatus.get(t.status as TaskStatus)?.push(t);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold">Tasks</h1>
        <p className="text-muted text-sm">Kanban view of the operating board.</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {COLUMNS.map((c) => {
          const items = byStatus.get(c.key) ?? [];
          return (
            <Panel
              key={c.key}
              title={`${c.label} (${items.length})`}
            >
              <div className="flex flex-col gap-2">
                {items.length === 0 ? (
                  <p className="text-xs text-muted">—</p>
                ) : (
                  items.map((t) => (
                    <div
                      key={t.id}
                      className="rounded border border-panelborder p-3 hover:border-accent/40 transition"
                    >
                      <div className="flex items-center justify-between">
                        <span className={`text-xs font-mono ${PRIORITY_COLOR[t.priority] ?? ''}`}>
                          {t.priority}
                        </span>
                        <span className="text-xs text-muted">#{shortId(t.id)}</span>
                      </div>
                      <div className="text-sm mt-1">{t.title}</div>
                      <div className="text-xs text-muted mt-1">owner: {t.agent_id}</div>
                    </div>
                  ))
                )}
              </div>
            </Panel>
          );
        })}
      </div>
    </div>
  );
}
