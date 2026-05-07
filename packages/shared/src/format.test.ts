import { describe, it, expect } from 'vitest';
import {
  escapeMarkdown,
  formatAgentResponse,
  formatBoardSummary,
  formatTaskList,
  shortId,
  truncate,
} from './format.js';

describe('format', () => {
  it('truncates with ellipsis', () => {
    expect(truncate('hello world', 5)).toBe('hell…');
    expect(truncate('hi', 5)).toBe('hi');
  });

  it('escapes markdown control chars', () => {
    expect(escapeMarkdown('hello *world* _again_')).toBe('hello \\*world\\* \\_again\\_');
  });

  it('formats agent response with bold label', () => {
    const out = formatAgentResponse('cto', 'plan: do x');
    expect(out).toContain('*Forge (CTO)*');
    expect(out).toContain('plan: do x');
  });

  it('formats board summary with synthesis and action plan', () => {
    const out = formatBoardSummary({
      input: 'should we build feature X?',
      responses: [
        {
          agent_id: 'cto',
          round: 1,
          content: 'feasible in 2 weeks',
          tokens_in: 0,
          tokens_out: 0,
          latency_ms: 0,
        },
      ],
      synthesis: 'ship it.',
      action_plan: '1. start monday',
    });
    expect(out).toContain('Boardroom on:');
    expect(out).toContain('Forge (CTO)');
    expect(out).toContain('ship it.');
    expect(out).toContain('Action plan');
  });

  it('formats empty task list with placeholder', () => {
    expect(formatTaskList([])).toMatch(/No open tasks/);
  });

  it('formats task list with priority icons and short ids', () => {
    const out = formatTaskList([
      {
        id: '12345678-aaaa-bbbb-cccc-ddddeeeeffff',
        title: 'cold DM script',
        description: null,
        agent_id: 'sales',
        status: 'open',
        priority: 'high',
        due_date: null,
        created_by: null,
        source_message_id: null,
        dependencies: [],
        progress_notes: null,
        created_at: '',
        updated_at: '',
        completed_at: null,
      },
    ]);
    expect(out).toContain('▲');
    expect(out).toContain('cold DM script');
    expect(out).toContain('#12345678');
  });

  it('shortens uuids to 8 hex chars', () => {
    expect(shortId('12345678-aaaa-bbbb-cccc-ddddeeeeffff')).toBe('12345678');
  });
});
