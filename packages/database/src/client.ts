import postgres from 'postgres';
import { loadEnv } from '@agentboard/config';

let _sql: postgres.Sql | null = null;

export function getSql(): postgres.Sql {
  if (_sql) return _sql;
  const env = loadEnv();
  if (!env.DATABASE_URL) {
    throw new Error('DATABASE_URL is required to use the database client.');
  }
  _sql = postgres(env.DATABASE_URL, {
    max: 10,
    idle_timeout: 20,
    connect_timeout: 30,
    prepare: false,
  });
  return _sql;
}

export async function closeSql() {
  if (_sql) {
    await _sql.end({ timeout: 5 });
    _sql = null;
  }
}
