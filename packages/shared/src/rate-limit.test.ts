import { describe, it, expect } from 'vitest';
import { RateLimiter } from './rate-limit.js';

describe('RateLimiter', () => {
  it('allows up to perMinute then blocks', () => {
    const r = new RateLimiter(3, 60_000);
    expect(r.allow('u1', 0)).toBe(true);
    expect(r.allow('u1', 1)).toBe(true);
    expect(r.allow('u1', 2)).toBe(true);
    expect(r.allow('u1', 3)).toBe(false);
  });

  it('refills over time', () => {
    const r = new RateLimiter(3, 60_000);
    expect(r.allow('u1', 0)).toBe(true);
    expect(r.allow('u1', 1)).toBe(true);
    expect(r.allow('u1', 2)).toBe(true);
    expect(r.allow('u1', 3)).toBe(false);
    // After 30s, refill 1.5 tokens; one more allowed
    expect(r.allow('u1', 30_000)).toBe(true);
    expect(r.allow('u1', 30_001)).toBe(false);
  });

  it('keeps users isolated', () => {
    const r = new RateLimiter(1, 60_000);
    expect(r.allow('a', 0)).toBe(true);
    expect(r.allow('a', 0)).toBe(false);
    expect(r.allow('b', 0)).toBe(true);
  });
});
