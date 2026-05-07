import { describe, it, expect } from 'vitest';
import { quickRoute, routeMessage } from './router.js';

describe('quickRoute', () => {
  it('routes panic keyword to panic mode with CTO+CEO+Ops', () => {
    const r = quickRoute('the queue is on fire, urgent help')!;
    expect(r.mode).toBe('panic');
    expect(r.urgency).toBe('urgent');
    expect(r.agents).toEqual(expect.arrayContaining(['cto', 'ceo', 'ops']));
  });

  it('routes "everyone weigh in" to board', () => {
    const r = quickRoute('Everyone weigh in on the new pricing')!;
    expect(r.mode).toBe('board');
  });

  it('routes "Atlas, …" direct address to single CEO', () => {
    const r = quickRoute('Atlas, what should we do this week?')!;
    expect(r.mode).toBe('single');
    expect(r.agents).toEqual(['ceo']);
  });

  it('routes "Forge —" direct address to single CTO', () => {
    const r = quickRoute('Forge — design the scraper')!;
    expect(r.mode).toBe('single');
    expect(r.agents).toEqual(['cto']);
  });

  it('routes "make this sell" to sales+marketing board', () => {
    const r = quickRoute('Make this sell, the offer is bad')!;
    expect(r.mode).toBe('board');
    expect(r.agents).toEqual(expect.arrayContaining(['sales', 'marketing']));
  });

  it('routes "turn this into tasks" to ops with create_task=true', () => {
    const r = quickRoute('Turn this into tasks please')!;
    expect(r.mode).toBe('single');
    expect(r.agents).toEqual(['ops']);
    expect(r.create_task).toBe(true);
  });

  it('routes "remember this" to memory mode', () => {
    const r = quickRoute('remember this: stripe is the payments stack')!;
    expect(r.mode).toBe('memory');
    expect(r.store_memory).toBe(true);
  });

  it('routes debate keyword', () => {
    const r = quickRoute('Debate hire vs build')!;
    expect(r.mode).toBe('debate');
  });

  it('routes decision keyword', () => {
    const r = quickRoute('Decide whether to ship v1')!;
    expect(r.mode).toBe('decision');
  });

  it('flags urgency from "asap"', () => {
    const r = quickRoute('Atlas, kill the v1 ASAP')!;
    expect(r.urgency).toBe('urgent');
  });

  it('returns null for ambiguous text (no rule match)', () => {
    expect(quickRoute('hmm just thinking about stuff')).toBeNull();
  });
});

describe('routeMessage', () => {
  it('falls back to default CEO when no rule matches and no AI provided', async () => {
    const r = await routeMessage('hmm just thinking about stuff');
    expect(r.mode).toBe('single');
    expect(r.agents).toEqual(['ceo']);
  });
});
