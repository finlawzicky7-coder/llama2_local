import { describe, it, expect } from 'vitest';
import { ALL_AGENTS, AGENT_DEFS, getStaticAgentRegistry } from './index.js';

describe('agent registry (static)', () => {
  it('has all five agents', () => {
    expect(ALL_AGENTS.map((a) => a.id).sort()).toEqual(
      ['ceo', 'cto', 'marketing', 'ops', 'sales'].sort(),
    );
  });

  it('decision weights are in [0, 1]', () => {
    for (const a of ALL_AGENTS) {
      expect(a.decision_weight).toBeGreaterThanOrEqual(0);
      expect(a.decision_weight).toBeLessThanOrEqual(1);
    }
  });

  it('each agent has a non-trivial system prompt', () => {
    for (const a of ALL_AGENTS) {
      expect(a.system_prompt.length).toBeGreaterThan(80);
      expect(a.system_prompt.toLowerCase()).toContain(a.name.toLowerCase());
    }
  });

  it('static registry returns code definitions when DB unavailable', () => {
    const reg = getStaticAgentRegistry();
    const ceo = reg.get('ceo');
    expect(ceo.name).toBe('Atlas');
    expect(ceo.system_prompt).toBe(AGENT_DEFS.ceo.system_prompt);
  });
});
