import { describe, it, expect } from 'vitest';
import { redact } from './redact.js';

describe('redact', () => {
  it('redacts known secret keys', () => {
    expect(
      redact({
        ANTHROPIC_API_KEY: 'sk-abc',
        TELEGRAM_BOT_TOKEN: '123:abc',
        nested: { SUPABASE_SERVICE_ROLE_KEY: 'srv', other: 'fine' },
      }),
    ).toEqual({
      ANTHROPIC_API_KEY: '[REDACTED]',
      TELEGRAM_BOT_TOKEN: '[REDACTED]',
      nested: { SUPABASE_SERVICE_ROLE_KEY: '[REDACTED]', other: 'fine' },
    });
  });

  it('redacts Bearer tokens in arbitrary strings', () => {
    expect(redact({ auth: 'Bearer abc.def.ghi' })).toEqual({ auth: 'Bearer [REDACTED]' });
  });

  it('passes through primitives and arrays', () => {
    expect(redact('hello')).toBe('hello');
    expect(redact(42)).toBe(42);
    expect(redact([1, 2, 3])).toEqual([1, 2, 3]);
  });
});
