interface Bucket {
  tokens: number;
  updated: number;
}

export class RateLimiter {
  private buckets = new Map<string | number, Bucket>();

  constructor(
    private readonly perMinute: number,
    private readonly windowMs: number = 60_000,
  ) {}

  /** Returns true if the action is allowed. */
  allow(key: string | number, now = Date.now()): boolean {
    const b = this.buckets.get(key) ?? { tokens: this.perMinute, updated: now };
    const elapsed = now - b.updated;
    if (elapsed > 0) {
      const refill = (elapsed / this.windowMs) * this.perMinute;
      b.tokens = Math.min(this.perMinute, b.tokens + refill);
      b.updated = now;
    }
    if (b.tokens >= 1) {
      b.tokens -= 1;
      this.buckets.set(key, b);
      return true;
    }
    this.buckets.set(key, b);
    return false;
  }

  reset(key: string | number) {
    this.buckets.delete(key);
  }
}
