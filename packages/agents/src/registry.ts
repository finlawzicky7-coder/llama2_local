import type { AgentId } from '@agentboard/shared';
import { listAgents, type AgentRow } from '@agentboard/database';
import { AGENT_DEFS, type AgentDefinition } from './definitions.js';

let cached: AgentRow[] | null = null;

/**
 * The registry merges the in-code agent definitions (personality, weights,
 * allowed actions) with the DB row (system_prompt may be edited via the
 * dashboard). DB wins on prompt; code wins on shape.
 */
export class AgentRegistry {
  private dbRows: Map<AgentId, AgentRow> = new Map();

  async load() {
    if (!cached) {
      try {
        cached = await listAgents();
      } catch {
        cached = [];
      }
    }
    for (const row of cached!) this.dbRows.set(row.id, row);
    return this;
  }

  list(): AgentDefinition[] {
    return Object.values(AGENT_DEFS).map((def) => this.merge(def));
  }

  get(id: AgentId): AgentDefinition {
    const def = AGENT_DEFS[id];
    return this.merge(def);
  }

  private merge(def: AgentDefinition): AgentDefinition {
    const row = this.dbRows.get(def.id);
    if (!row) return def;
    return {
      ...def,
      name: row.name || def.name,
      role: row.role || def.role,
      personality: row.personality || def.personality,
      system_prompt: row.system_prompt || def.system_prompt,
      decision_weight: row.decision_weight ?? def.decision_weight,
    };
  }
}

let _registry: AgentRegistry | null = null;
export async function getAgentRegistry(): Promise<AgentRegistry> {
  if (_registry) return _registry;
  _registry = await new AgentRegistry().load();
  return _registry;
}

/** For tests + offline dev, provides a registry that doesn't touch the DB. */
export function getStaticAgentRegistry(): AgentRegistry {
  const r = new AgentRegistry();
  return r;
}
