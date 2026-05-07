import { describe, it, expect } from 'vitest';
import { agentDisplayName, agentLabel, resolveAgent } from './agent-aliases.js';

describe('agent aliases', () => {
  it('resolves canonical IDs', () => {
    expect(resolveAgent('ceo')).toBe('ceo');
    expect(resolveAgent('cto')).toBe('cto');
    expect(resolveAgent('sales')).toBe('sales');
    expect(resolveAgent('marketing')).toBe('marketing');
    expect(resolveAgent('ops')).toBe('ops');
  });

  it('resolves names, case insensitive, with whitespace', () => {
    expect(resolveAgent('Atlas')).toBe('ceo');
    expect(resolveAgent(' Forge ')).toBe('cto');
    expect(resolveAgent('VIPER')).toBe('sales');
    expect(resolveAgent('Nova')).toBe('marketing');
    expect(resolveAgent('Ledger')).toBe('ops');
  });

  it('returns null for unknown', () => {
    expect(resolveAgent('nobody')).toBeNull();
  });

  it('formats display label', () => {
    expect(agentDisplayName('ceo')).toBe('Atlas');
    expect(agentLabel('ops')).toBe('Ledger (Ops)');
  });
});
