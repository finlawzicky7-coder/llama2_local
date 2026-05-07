const SECRET_KEYS = [
  'ANTHROPIC_API_KEY',
  'TELEGRAM_BOT_TOKEN',
  'TELEGRAM_WEBHOOK_SECRET',
  'SUPABASE_SERVICE_ROLE_KEY',
  'SUPABASE_ANON_KEY',
  'EMBEDDING_API_KEY',
  'DATABASE_URL',
  'REDIS_URL',
];

export function redact<T>(input: T): T {
  if (input === null || typeof input !== 'object') return input;
  if (Array.isArray(input)) {
    return input.map(redact) as unknown as T;
  }
  const out: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(input as Record<string, unknown>)) {
    if (SECRET_KEYS.includes(k.toUpperCase())) {
      out[k] = '[REDACTED]';
    } else if (typeof v === 'string' && /Bearer\s+\S+/i.test(v)) {
      out[k] = v.replace(/Bearer\s+\S+/gi, 'Bearer [REDACTED]');
    } else {
      out[k] = redact(v);
    }
  }
  return out as T;
}
