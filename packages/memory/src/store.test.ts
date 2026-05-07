import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock the database functions used by MemoryStore.
const inserted: Array<Record<string, unknown>> = [];
let storedSearchHits: Array<Record<string, unknown>> = [];

vi.mock('@agentboard/database', () => ({
  insertMemory: vi.fn(async (args: Record<string, unknown>) => {
    const row = {
      id: `mem-${inserted.length + 1}`,
      type: args.type,
      content: args.content,
      summary: args.summary,
      importance_score: args.importance_score,
      source: args.source,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      expires_at: null,
      metadata: args.metadata ?? {},
    };
    inserted.push(row);
    return row;
  }),
  searchMemories: vi.fn(async () => storedSearchHits),
  listMemories: vi.fn(async () => inserted),
  deleteMemory: vi.fn(async () => {}),
}));

vi.mock('@agentboard/ai', () => ({
  getEmbeddingProvider: () => ({
    dim: () => 8,
    createEmbedding: async (text: string) => ({
      embedding: new Array(8).fill(text.length % 5),
      model: 'mock',
      tokens: 0,
      cost_usd: 0,
    }),
  }),
}));

import { MemoryStore } from './index.js';

describe('MemoryStore', () => {
  beforeEach(() => {
    inserted.length = 0;
    storedSearchHits = [];
  });

  it('stores when no near-duplicate', async () => {
    const store = new MemoryStore();
    const r = await store.store({ type: 'business_context', content: 'we use stripe' });
    expect(r.deduped).toBe(false);
    expect(inserted).toHaveLength(1);
  });

  it('dedups when an existing memory is near-identical', async () => {
    storedSearchHits = [
      {
        id: 'mem-existing',
        type: 'business_context',
        content: 'stripe is the payments stack',
        summary: 'stripe',
        importance_score: 0.7,
        source: null,
        created_at: '',
        updated_at: '',
        expires_at: null,
        metadata: {},
        similarity: 0.95,
      },
    ];
    const store = new MemoryStore();
    const r = await store.store({ type: 'business_context', content: 'stripe payments stack' });
    expect(r.deduped).toBe(true);
    expect(inserted).toHaveLength(0);
  });

  it('rejects too-short content via Zod', async () => {
    const store = new MemoryStore();
    await expect(store.store({ type: 'system_note', content: 'a' })).rejects.toThrow();
  });
});
