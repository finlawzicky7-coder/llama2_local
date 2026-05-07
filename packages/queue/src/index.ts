import { loadEnv } from '@agentboard/config';
import { createLogger } from '@agentboard/shared';

const log = createLogger('queue');

export interface JobQueue<TPayload, TResult> {
  enqueue(name: string, payload: TPayload): Promise<{ id: string }>;
  process(name: string, handler: (payload: TPayload) => Promise<TResult>): void;
  close(): Promise<void>;
}

class InProcessQueue<TPayload, TResult> implements JobQueue<TPayload, TResult> {
  private handlers = new Map<string, (payload: TPayload) => Promise<TResult>>();
  private counter = 0;

  async enqueue(name: string, payload: TPayload) {
    const id = String(++this.counter);
    const handler = this.handlers.get(name);
    if (!handler) {
      log.warn('No handler registered for in-process job; running noop', { name });
      return { id };
    }
    // Run synchronously but in a microtask so callers can await enqueue cheaply.
    queueMicrotask(() => {
      handler(payload).catch((err) =>
        log.error('In-process job failed', { name, err: String(err) }),
      );
    });
    return { id };
  }

  process(name: string, handler: (payload: TPayload) => Promise<TResult>) {
    this.handlers.set(name, handler);
  }

  async close() {
    this.handlers.clear();
  }
}

class BullQueueImpl<TPayload, TResult> implements JobQueue<TPayload, TResult> {
  private queues = new Map<string, unknown>();
  private workers: unknown[] = [];
  private connection: unknown;

  constructor(redisUrl: string) {
    // Lazy-load to avoid loading bullmq when redis isn't configured.
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const { Queue, Worker } = require('bullmq') as typeof import('bullmq');
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const Redis = require('ioredis') as typeof import('ioredis');
    this.connection = new Redis.default(redisUrl, { maxRetriesPerRequest: null });
    (this as { _Queue?: unknown })._Queue = Queue;
    (this as { _Worker?: unknown })._Worker = Worker;
  }

  private get Queue() {
    return (this as { _Queue?: typeof import('bullmq').Queue })._Queue!;
  }
  private get Worker() {
    return (this as { _Worker?: typeof import('bullmq').Worker })._Worker!;
  }

  private getQueue(name: string) {
    const existing = this.queues.get(name);
    if (existing) return existing as InstanceType<typeof import('bullmq').Queue>;
    const QueueCtor = this.Queue as unknown as typeof import('bullmq').Queue;
    const q = new QueueCtor(name, { connection: this.connection as never });
    this.queues.set(name, q);
    return q;
  }

  async enqueue(name: string, payload: TPayload) {
    const job = await this.getQueue(name).add(name, payload as object);
    return { id: String(job.id) };
  }

  process(name: string, handler: (payload: TPayload) => Promise<TResult>) {
    const WorkerCtor = this.Worker as unknown as typeof import('bullmq').Worker;
    const worker = new WorkerCtor(
      name,
      async (job) => handler(job.data as TPayload),
      { connection: this.connection as never },
    );
    worker.on('failed', (job, err) =>
      log.error('queue job failed', { name, id: job?.id, err: String(err) }),
    );
    this.workers.push(worker);
  }

  async close() {
    for (const w of this.workers) {
      try { await (w as { close: () => Promise<void> }).close(); } catch { /* ignore */ }
    }
    for (const q of this.queues.values()) {
      try { await (q as { close: () => Promise<void> }).close(); } catch { /* ignore */ }
    }
    try { await (this.connection as { quit: () => Promise<void> }).quit(); } catch { /* ignore */ }
  }
}

let _queue: JobQueue<unknown, unknown> | null = null;

export function getQueue<TPayload = unknown, TResult = unknown>(): JobQueue<TPayload, TResult> {
  if (_queue) return _queue as JobQueue<TPayload, TResult>;
  const env = loadEnv();
  if (env.REDIS_URL) {
    try {
      _queue = new BullQueueImpl<unknown, unknown>(env.REDIS_URL);
      log.info('using BullMQ queue', { redis: env.REDIS_URL.replace(/\/\/.*@/, '//<creds>@') });
    } catch (err) {
      log.warn('BullMQ unavailable, falling back to in-process queue', { err: String(err) });
      _queue = new InProcessQueue<unknown, unknown>();
    }
  } else {
    _queue = new InProcessQueue<unknown, unknown>();
    log.info('REDIS_URL unset — using in-process queue (dev mode).');
  }
  return _queue as JobQueue<TPayload, TResult>;
}
