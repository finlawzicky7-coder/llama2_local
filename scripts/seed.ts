#!/usr/bin/env tsx
/** Re-run only the seed file (agents). */
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import postgres from 'postgres';
import { loadEnv } from '../packages/config/src/index.js';

async function main() {
  const env = loadEnv();
  if (!env.DATABASE_URL) throw new Error('DATABASE_URL required');
  const sql = postgres(env.DATABASE_URL, { prepare: false });
  const text = readFileSync(resolve(process.cwd(), 'supabase', 'seed.sql'), 'utf8');
  await sql.unsafe(text);
  await sql.end({ timeout: 5 });
  console.log('Seeded.');
}
main().catch((e) => {
  console.error(e);
  process.exit(1);
});
