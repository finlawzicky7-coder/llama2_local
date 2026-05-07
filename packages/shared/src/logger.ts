import { redact } from './redact.js';

export type LogLevel = 'debug' | 'info' | 'warn' | 'error';
const ORDER: Record<LogLevel, number> = { debug: 10, info: 20, warn: 30, error: 40 };

const envLevel = (process.env.LOG_LEVEL as LogLevel) || 'info';

function emit(level: LogLevel, source: string, msg: string, data?: unknown) {
  if (ORDER[level] < ORDER[envLevel]) return;
  const entry = {
    t: new Date().toISOString(),
    level,
    source,
    msg,
    ...(data !== undefined ? { data: redact(data) } : {}),
  };
  // Single-line JSON keeps logs grep-able and safe.
  // eslint-disable-next-line no-console
  console.log(JSON.stringify(entry));
}

export function createLogger(source: string) {
  return {
    debug: (msg: string, data?: unknown) => emit('debug', source, msg, data),
    info: (msg: string, data?: unknown) => emit('info', source, msg, data),
    warn: (msg: string, data?: unknown) => emit('warn', source, msg, data),
    error: (msg: string, data?: unknown) => emit('error', source, msg, data),
  };
}
