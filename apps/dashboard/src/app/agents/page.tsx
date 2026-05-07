import { listAgents } from '@agentboard/database';
import { ALL_AGENTS } from '@agentboard/agents';
import { Panel } from '@/components/sidebar';
import { safe } from '@/lib/safe';

export const dynamic = 'force-dynamic';

export default async function AgentsPage() {
  const dbRows = await safe(() => listAgents(), []);
  const merged = ALL_AGENTS.map((def) => {
    const row = dbRows.find((r) => r.id === def.id);
    return {
      id: def.id,
      name: row?.name ?? def.name,
      role: row?.role ?? def.role,
      personality: row?.personality ?? def.personality,
      decision_weight: row?.decision_weight ?? def.decision_weight,
      status: row?.status ?? 'active',
      allowed_actions: def.allowed_actions,
    };
  });

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold">Agents</h1>
        <p className="text-muted text-sm">The five-member board.</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {merged.map((a) => (
          <Panel
            key={a.id}
            title={`${a.name} — ${a.role}`}
            right={
              <span
                className={`text-xs px-2 py-1 rounded ${
                  a.status === 'active'
                    ? 'bg-good/10 text-good'
                    : 'bg-warn/10 text-warn'
                }`}
              >
                {a.status}
              </span>
            }
          >
            <p className="text-sm text-muted mb-3">{a.personality}</p>
            <div className="text-xs text-muted">
              <div>weight: {a.decision_weight.toFixed(2)}</div>
              <div>actions: {a.allowed_actions.join(', ')}</div>
            </div>
          </Panel>
        ))}
      </div>
    </div>
  );
}
