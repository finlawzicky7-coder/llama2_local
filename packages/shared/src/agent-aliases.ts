import type { AgentId } from './types.js';

export const AGENT_ALIASES: Record<string, AgentId> = {
  ceo: 'ceo',
  atlas: 'ceo',
  founder: 'ceo',

  cto: 'cto',
  forge: 'cto',
  eng: 'cto',
  engineer: 'cto',
  tech: 'cto',

  sales: 'sales',
  viper: 'sales',
  closer: 'sales',
  bd: 'sales',

  marketing: 'marketing',
  nova: 'marketing',
  growth: 'marketing',
  mkt: 'marketing',

  ops: 'ops',
  ledger: 'ops',
  pm: 'ops',
  operations: 'ops',
};

export function resolveAgent(input: string): AgentId | null {
  const k = input.trim().toLowerCase();
  return AGENT_ALIASES[k] ?? null;
}

const NAME_BY_ID: Record<AgentId, string> = {
  ceo: 'Atlas',
  cto: 'Forge',
  sales: 'Viper',
  marketing: 'Nova',
  ops: 'Ledger',
};

export const ROLE_BY_ID: Record<AgentId, string> = {
  ceo: 'CEO',
  cto: 'CTO',
  sales: 'Sales',
  marketing: 'Marketing',
  ops: 'Ops',
};

export function agentDisplayName(id: AgentId): string {
  return NAME_BY_ID[id];
}

export function agentLabel(id: AgentId): string {
  return `${NAME_BY_ID[id]} (${ROLE_BY_ID[id]})`;
}
