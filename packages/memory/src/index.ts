import { getEmbeddingProvider } from '@agentboard/ai';
import {
  insertMemory,
  searchMemories,
  listMemories,
  deleteMemory,
} from '@agentboard/database';
import {
  CreateMemoryInput,
  RecallInput,
  type CreateMemory,
  type Memory,
} from '@agentboard/shared';

const DEDUP_THRESHOLD = 0.92;

export interface RecalledMemory extends Memory {
  similarity: number;
}

export class MemoryStore {
  /**
   * Insert a memory. If a near-duplicate (cosine ≥ 0.92) already exists,
   * skip insert and return the existing record (importance bumped).
   */
  async store(input: CreateMemory): Promise<{ memory: Memory; deduped: boolean }> {
    const parsed = CreateMemoryInput.parse(input);
    const embed = await getEmbeddingProvider().createEmbedding(
      parsed.summary ? `${parsed.summary}\n\n${parsed.content}` : parsed.content,
    );
    const existing = await searchMemories({
      embedding: embed.embedding,
      top_k: 1,
      min_similarity: DEDUP_THRESHOLD,
    });
    if (existing.length > 0 && existing[0]) {
      return { memory: existing[0], deduped: true };
    }
    const memory = await insertMemory({ ...parsed, embedding: embed.embedding });
    return { memory, deduped: false };
  }

  /** Vector recall. */
  async recall(args: { query: string; top_k?: number; min_similarity?: number }) {
    const parsed = RecallInput.parse(args);
    const embed = await getEmbeddingProvider().createEmbedding(parsed.query);
    return searchMemories({
      embedding: embed.embedding,
      top_k: parsed.top_k,
      min_similarity: parsed.min_similarity,
    });
  }

  async list(limit = 50) {
    return listMemories(limit);
  }

  async delete(id: string) {
    await deleteMemory(id);
  }
}

let _store: MemoryStore | null = null;
export function getMemoryStore(): MemoryStore {
  if (!_store) _store = new MemoryStore();
  return _store;
}

/** Format a list of recalled memories for inclusion in an agent prompt. */
export function formatMemoriesForPrompt(memories: RecalledMemory[]): string {
  if (!memories.length) return '';
  const lines = memories.map((m, i) => {
    const head = m.summary ? m.summary.trim() : m.content.slice(0, 200).trim();
    return `[${i + 1}] (${m.type}, importance=${m.importance_score.toFixed(2)}, sim=${m.similarity.toFixed(2)}) ${head}`;
  });
  return [
    '<relevant_memory>',
    'These are memories the operator has stored. Use them when they are relevant. Do not repeat them verbatim unless asked.',
    ...lines,
    '</relevant_memory>',
  ].join('\n');
}
