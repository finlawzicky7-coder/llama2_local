import { describe, it, expect, vi, beforeEach } from 'vitest';
import { runBoard, runDebate, runDecision, runPanic, runSingle } from './engine.js';
import { getStaticAgentRegistry } from '@agentboard/agents';
import type { AIProvider } from '@agentboard/ai';

// All DB calls in the engine come from @agentboard/database. We mock the
// whole module so the engine logic can be tested without a Postgres.
vi.mock('@agentboard/database', () => {
  const recorded: Record<string, unknown[]> = {
    runs: [],
    responses: [],
    internal: [],
    finished: [],
  };
  return {
    startRun: vi.fn(async (args: Record<string, unknown>) => {
      const id = `run-${recorded.runs.length + 1}`;
      recorded.runs.push({ id, ...args });
      return { id, ...args };
    }),
    finishRun: vi.fn(async (id: string, args: unknown) => {
      recorded.finished.push({ id, ...((args as object) ?? {}) });
    }),
    recordAgentResponse: vi.fn(async (args: unknown) => {
      recorded.responses.push(args);
    }),
    recordInternalAgentMessage: vi.fn(async (args: unknown) => {
      recorded.internal.push(args);
    }),
    recordApiUsage: vi.fn(async () => {}),
    recentMessagesForChat: vi.fn(async () => []),
    listTasks: vi.fn(async () => []),
    listMemories: vi.fn(async () => []),
    __recorded: recorded,
  };
});

vi.mock('@agentboard/memory', () => ({
  getMemoryStore: () => ({
    recall: async () => [],
    store: async () => ({ memory: { id: 'm1' }, deduped: false }),
  }),
  formatMemoriesForPrompt: () => '',
}));

const fakeAI: AIProvider = {
  async generateText(args) {
    // Echo a tag indicating which agent was asked, useful for assertions.
    const sysHead = args.system.slice(0, 80);
    return {
      text: `OK from system: ${sysHead.split('\n')[0]} | input: ${args.messages[args.messages.length - 1]?.content?.slice(0, 60)}`,
      model: 'fake',
      tokens_in: 50,
      tokens_out: 30,
      cost_usd: 0.001,
      latency_ms: 5,
    };
  },
  async generateStructured(args) {
    const raw = await this.generateText(args);
    return { value: args.parse(raw.text), raw };
  },
  estimateCost: () => 0.001,
};

const ctx = {
  ai: fakeAI,
  registry: getStaticAgentRegistry(),
  chat_id: 1,
  user_id: 1,
};

describe('orchestrator engine', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('runSingle returns the agent response', async () => {
    const r = await runSingle(ctx, { agent: 'ceo', message: 'plan q4' });
    expect(r.status).toBe('succeeded');
    expect(r.responses).toHaveLength(1);
    expect(r.responses[0]!.agent_id).toBe('ceo');
    expect(r.responses[0]!.content).toContain('Atlas');
  });

  it('runBoard fans out to all agents and adds CEO synth + Ops plan', async () => {
    const r = await runBoard(ctx, { message: 'should we ship?' });
    expect(r.status).toBe('succeeded');
    // 5 round-1 + CEO synth + Ops plan
    expect(r.responses.length).toBeGreaterThanOrEqual(7);
    expect(r.synthesis).toBeTruthy();
    expect(r.action_plan).toBeTruthy();
  });

  it('runDebate runs 3 rounds plus final + plan', async () => {
    const r = await runDebate(ctx, { message: 'hire vs build?' });
    expect(r.status).toBe('succeeded');
    // 5 agents x 3 rounds = 15, plus final + plan = 17
    expect(r.responses.length).toBe(17);
    expect(r.decision).toBeTruthy();
    expect(r.action_plan).toBeTruthy();
  });

  it('runDecision returns inputs + decision + next', async () => {
    const r = await runDecision(ctx, { message: 'ship v1?' });
    // 5 inputs + 1 decision + 1 next
    expect(r.responses.length).toBe(7);
    expect(r.decision).toBeTruthy();
    expect(r.next_actions).toBeTruthy();
  });

  it('runPanic returns CTO+CEO+Ops trio', async () => {
    const r = await runPanic(ctx, { problem: 'queue dead' });
    expect(r.responses.length).toBe(3);
    expect(r.responses.map((x) => x.agent_id).sort()).toEqual(['ceo', 'cto', 'ops']);
  });

  it('continues with partial status when one agent fails', async () => {
    const flaky: AIProvider = {
      ...fakeAI,
      async generateText(args) {
        if (args.system.toLowerCase().startsWith('you are viper')) {
          throw new Error('boom');
        }
        return fakeAI.generateText(args);
      },
    };
    const r = await runBoard({ ...ctx, ai: flaky }, { message: 'should we ship?' });
    expect(['partial', 'succeeded']).toContain(r.status);
    expect(r.partial_failures).toContain('sales');
  });
});
