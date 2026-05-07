export interface AIMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface GenerateTextArgs {
  system: string;
  messages: AIMessage[];
  model?: string;
  max_tokens?: number;
  temperature?: number;
  stop_sequences?: string[];
}

export interface GenerateTextResult {
  text: string;
  model: string;
  tokens_in: number;
  tokens_out: number;
  cost_usd: number;
  latency_ms: number;
}

export interface GenerateStructuredArgs<T> extends GenerateTextArgs {
  parse: (text: string) => T;
}

export interface EmbeddingResult {
  embedding: number[];
  model: string;
  tokens: number;
  cost_usd: number;
}

export interface AIProvider {
  generateText(args: GenerateTextArgs): Promise<GenerateTextResult>;
  generateStructured<T>(args: GenerateStructuredArgs<T>): Promise<{
    value: T;
    raw: GenerateTextResult;
  }>;
  estimateCost(model: string, tokens_in: number, tokens_out: number): number;
}

export interface EmbeddingProvider {
  createEmbedding(text: string): Promise<EmbeddingResult>;
  dim(): number;
}
