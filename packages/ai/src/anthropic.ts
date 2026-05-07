import Anthropic from '@anthropic-ai/sdk';
import { loadEnv } from '@agentboard/config';
import { withRetry } from '@agentboard/shared';
import type {
  AIProvider,
  GenerateStructuredArgs,
  GenerateTextArgs,
  GenerateTextResult,
} from './types.js';

// Approximate prices in USD per 1M tokens. Used for cost telemetry only.
// Edit when Anthropic publishes new prices for the chosen model.
const PRICES: Record<string, { in: number; out: number }> = {
  'claude-sonnet-4-6': { in: 3, out: 15 },
  'claude-opus-4-7':   { in: 15, out: 75 },
  'claude-haiku-4-5':  { in: 0.8, out: 4 },
  'claude-3-5-sonnet-20241022': { in: 3, out: 15 },
};

function priceFor(model: string) {
  return (
    PRICES[model] ||
    Object.entries(PRICES).find(([k]) => model.startsWith(k))?.[1] ||
    PRICES['claude-sonnet-4-6']!
  );
}

export class AnthropicProvider implements AIProvider {
  private client: Anthropic;
  private defaultModel: string;

  constructor(apiKey?: string, defaultModel?: string) {
    const env = loadEnv();
    const key = apiKey ?? env.ANTHROPIC_API_KEY;
    if (!key) throw new Error('ANTHROPIC_API_KEY is required for AnthropicProvider.');
    this.client = new Anthropic({ apiKey: key });
    this.defaultModel = defaultModel ?? env.DEFAULT_MODEL;
  }

  estimateCost(model: string, tokens_in: number, tokens_out: number): number {
    const p = priceFor(model);
    return (tokens_in * p.in + tokens_out * p.out) / 1_000_000;
  }

  async generateText(args: GenerateTextArgs): Promise<GenerateTextResult> {
    const model = args.model ?? this.defaultModel;
    const start = Date.now();
    const res = await withRetry(
      () =>
        this.client.messages.create({
          model,
          max_tokens: args.max_tokens ?? 1024,
          temperature: args.temperature ?? 0.7,
          system: args.system,
          messages: args.messages.map((m) => ({
            role: m.role === 'system' ? 'user' : m.role,
            content: m.content,
          })),
          stop_sequences: args.stop_sequences,
        }),
      { attempts: 3, baseDelayMs: 1000 },
    );
    const latency_ms = Date.now() - start;
    const text = res.content
      .map((c) => (c.type === 'text' ? c.text : ''))
      .join('')
      .trim();
    const tokens_in = res.usage?.input_tokens ?? 0;
    const tokens_out = res.usage?.output_tokens ?? 0;
    const cost_usd = this.estimateCost(model, tokens_in, tokens_out);
    return { text, model, tokens_in, tokens_out, cost_usd, latency_ms };
  }

  async generateStructured<T>(args: GenerateStructuredArgs<T>) {
    const raw = await this.generateText(args);
    const value = args.parse(raw.text);
    return { value, raw };
  }
}
