import { loadEnv } from '@agentboard/config';
import { withRetry } from '@agentboard/shared';
import type { EmbeddingProvider, EmbeddingResult } from './types.js';

/**
 * OpenAI-compatible embeddings client. Works with OpenAI, Together,
 * Groq, or any provider that exposes /v1/embeddings.
 */
export class OpenAIEmbeddings implements EmbeddingProvider {
  private model: string;
  private apiKey: string;
  private baseUrl: string;
  private dimension: number;

  constructor(opts: { apiKey?: string; model?: string; baseUrl?: string; dim?: number } = {}) {
    const env = loadEnv();
    this.apiKey = opts.apiKey ?? env.EMBEDDING_API_KEY ?? '';
    this.model = opts.model ?? env.EMBEDDING_MODEL;
    this.baseUrl = opts.baseUrl ?? 'https://api.openai.com/v1';
    this.dimension = opts.dim ?? env.EMBEDDING_DIM;
  }

  dim(): number {
    return this.dimension;
  }

  async createEmbedding(text: string): Promise<EmbeddingResult> {
    if (!this.apiKey) {
      throw new Error('EMBEDDING_API_KEY is required for the openai embedding provider.');
    }
    const res = await withRetry(
      async () => {
        const r = await fetch(`${this.baseUrl}/embeddings`, {
          method: 'POST',
          headers: {
            'content-type': 'application/json',
            authorization: `Bearer ${this.apiKey}`,
          },
          body: JSON.stringify({ model: this.model, input: text }),
        });
        if (!r.ok) {
          const body = await r.text();
          throw new Error(`Embeddings HTTP ${r.status}: ${body.slice(0, 400)}`);
        }
        return (await r.json()) as {
          data: Array<{ embedding: number[] }>;
          usage?: { total_tokens?: number };
        };
      },
      { attempts: 3, baseDelayMs: 1000 },
    );
    const embedding = res.data[0]!.embedding;
    if (embedding.length !== this.dimension) {
      // Truncate or pad to keep DB schema stable.
      const fixed = new Array<number>(this.dimension).fill(0);
      for (let i = 0; i < Math.min(embedding.length, this.dimension); i++) {
        fixed[i] = embedding[i] ?? 0;
      }
      return {
        embedding: fixed,
        model: this.model,
        tokens: res.usage?.total_tokens ?? 0,
        cost_usd: 0,
      };
    }
    return {
      embedding,
      model: this.model,
      tokens: res.usage?.total_tokens ?? 0,
      cost_usd: 0,
    };
  }
}

/**
 * Deterministic offline fallback. Hash-based pseudo-embedding so the
 * memory store still works in tests / offline dev. Not semantic.
 */
export class MockEmbeddings implements EmbeddingProvider {
  constructor(private dimension = 1536) {}

  dim() {
    return this.dimension;
  }

  async createEmbedding(text: string): Promise<EmbeddingResult> {
    const v = new Array<number>(this.dimension).fill(0);
    let h = 2166136261;
    for (let i = 0; i < text.length; i++) {
      h ^= text.charCodeAt(i);
      h = (h * 16777619) >>> 0;
      v[h % this.dimension] = (v[h % this.dimension]! + 1) % 5;
    }
    // L2 normalize for cosine compatibility.
    let norm = 0;
    for (const x of v) norm += x * x;
    norm = Math.sqrt(norm) || 1;
    return {
      embedding: v.map((x) => x / norm),
      model: 'mock',
      tokens: 0,
      cost_usd: 0,
    };
  }
}
