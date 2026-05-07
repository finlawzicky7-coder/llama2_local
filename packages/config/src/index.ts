import { config as loadDotenv } from 'dotenv';
import { z } from 'zod';

loadDotenv();

const csvNumber = z
  .string()
  .optional()
  .transform((s) =>
    (s ?? '')
      .split(',')
      .map((x) => x.trim())
      .filter(Boolean)
      .map((x) => Number(x))
      .filter((n) => Number.isFinite(n)),
  );

const Schema = z.object({
  NODE_ENV: z.enum(['development', 'test', 'production']).default('development'),
  LOG_LEVEL: z.enum(['debug', 'info', 'warn', 'error']).default('info'),

  ANTHROPIC_API_KEY: z.string().min(1).optional(),
  DEFAULT_MODEL: z.string().default('claude-sonnet-4-6'),

  TELEGRAM_BOT_TOKEN: z.string().min(1).optional(),
  TELEGRAM_WEBHOOK_SECRET: z.string().optional(),
  TELEGRAM_ADMIN_USER_IDS: csvNumber,
  TELEGRAM_MODE: z.enum(['polling', 'webhook']).default('polling'),
  TELEGRAM_WEBHOOK_URL: z.string().url().optional(),

  SUPABASE_URL: z.string().url().optional(),
  SUPABASE_SERVICE_ROLE_KEY: z.string().optional(),
  SUPABASE_ANON_KEY: z.string().optional(),
  DATABASE_URL: z.string().optional(),

  REDIS_URL: z.string().optional(),

  EMBEDDING_PROVIDER: z.enum(['openai', 'anthropic', 'mock']).default('openai'),
  EMBEDDING_API_KEY: z.string().optional(),
  EMBEDDING_MODEL: z.string().default('text-embedding-3-small'),
  EMBEDDING_DIM: z.coerce.number().int().positive().default(1536),

  DASHBOARD_URL: z.string().optional(),

  RATE_LIMIT_PER_MIN: z.coerce.number().int().positive().default(20),
});

export type AppEnv = z.infer<typeof Schema>;

let cached: AppEnv | null = null;

export function loadEnv(opts: { strict?: boolean } = {}): AppEnv {
  if (cached) return cached;
  const parsed = Schema.safeParse(process.env);
  if (!parsed.success) {
    const msg = parsed.error.issues
      .map((i) => `  - ${i.path.join('.')}: ${i.message}`)
      .join('\n');
    throw new Error(`Invalid environment variables:\n${msg}`);
  }
  if (opts.strict) {
    const required: Array<keyof AppEnv> = [
      'ANTHROPIC_API_KEY',
      'TELEGRAM_BOT_TOKEN',
      'DATABASE_URL',
    ];
    const missing = required.filter((k) => !parsed.data[k]);
    if (missing.length) {
      throw new Error(
        `Missing required env vars for production-like run: ${missing.join(', ')}.\n` +
          `Set them in .env or your deploy environment.`,
      );
    }
  }
  cached = parsed.data;
  return cached;
}

export function isAdmin(userId: number): boolean {
  const env = loadEnv();
  return env.TELEGRAM_ADMIN_USER_IDS.includes(userId);
}
