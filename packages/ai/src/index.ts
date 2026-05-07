import { loadEnv } from '@agentboard/config';
import { AnthropicProvider } from './anthropic.js';
import { MockEmbeddings, OpenAIEmbeddings } from './embeddings.js';
import type { AIProvider, EmbeddingProvider } from './types.js';

export * from './types.js';
export { AnthropicProvider } from './anthropic.js';
export { OpenAIEmbeddings, MockEmbeddings } from './embeddings.js';

let _ai: AIProvider | null = null;
let _embed: EmbeddingProvider | null = null;

export function getAIProvider(): AIProvider {
  if (_ai) return _ai;
  _ai = new AnthropicProvider();
  return _ai;
}

export function getEmbeddingProvider(): EmbeddingProvider {
  if (_embed) return _embed;
  const env = loadEnv();
  if (env.EMBEDDING_PROVIDER === 'mock' || !env.EMBEDDING_API_KEY) {
    _embed = new MockEmbeddings(env.EMBEDDING_DIM);
  } else {
    _embed = new OpenAIEmbeddings();
  }
  return _embed;
}
