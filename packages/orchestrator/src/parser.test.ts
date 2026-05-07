import { describe, it, expect } from 'vitest';
import { parseCommand } from './parser.js';

describe('parseCommand', () => {
  it('returns null for non-command messages', () => {
    expect(parseCommand('hello there')).toBeNull();
    expect(parseCommand('Atlas, what now?')).toBeNull();
  });

  it('parses /start and /help', () => {
    expect(parseCommand('/start')!.kind).toBe('start');
    expect(parseCommand('/help')!.kind).toBe('help');
  });

  it('parses /ask with agent alias', () => {
    const r = parseCommand('/ask cto build the scraper architecture');
    expect(r).toEqual({
      kind: 'ask',
      agent: 'cto',
      message: 'build the scraper architecture',
    });
    const r2 = parseCommand('/ask Forge urgent: design the queue');
    expect(r2).toEqual({ kind: 'ask', agent: 'cto', message: 'urgent: design the queue' });
  });

  it('rejects /ask with unknown agent', () => {
    const r = parseCommand('/ask nobody hi') as { kind: 'invalid' };
    expect(r.kind).toBe('invalid');
  });

  it('parses /board, /debate, /decision', () => {
    expect(parseCommand('/board what should I do?')!.kind).toBe('board');
    expect(parseCommand('/debate hire vs build')!.kind).toBe('debate');
    expect(parseCommand('/decision keep or kill the v1?')!.kind).toBe('decision');
  });

  it('parses /task with priority', () => {
    const r = parseCommand('/task sales high write cold DM script');
    expect(r).toEqual({
      kind: 'task',
      agent: 'sales',
      priority: 'high',
      title: 'write cold DM script',
    });
  });

  it('rejects /task with bad priority', () => {
    const r = parseCommand('/task sales asap write script') as { kind: 'invalid' };
    expect(r.kind).toBe('invalid');
  });

  it('parses /done with id', () => {
    expect(parseCommand('/done 1234abcd')).toEqual({ kind: 'done', id: '1234abcd' });
  });

  it('parses /memory and /recall', () => {
    expect(parseCommand('/memory we onboard via Stripe')!.kind).toBe('memory');
    expect(parseCommand('/recall stripe onboarding')!.kind).toBe('recall');
  });

  it('parses /panic /brief /mode', () => {
    expect(parseCommand('/panic the queue is dead')!.kind).toBe('panic');
    expect(parseCommand('/brief')!.kind).toBe('brief');
    expect(parseCommand('/mode aggressive')!.kind).toBe('mode');
  });

  it('handles bot-suffixed commands like /ask@MyBot', () => {
    const r = parseCommand('/ask@AgentBoardBot ceo strategy now');
    expect(r).toEqual({ kind: 'ask', agent: 'ceo', message: 'strategy now' });
  });

  it('returns unknown for /foo', () => {
    expect(parseCommand('/foo')!.kind).toBe('unknown');
  });
});
