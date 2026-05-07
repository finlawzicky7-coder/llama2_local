#!/usr/bin/env tsx
/**
 * Apply migrations + seed to the database referenced by DATABASE_URL.
 * Idempotent: re-running is safe.
 */
import { readFileSync, readdirSync } from 'node:fs';
import { join, resolve } from 'node:path';
import postgres from 'postgres';
import { loadEnv } from '../packages/config/src/index.js';

async function main() {
  const env = loadEnv();
  if (!env.DATABASE_URL) {
    console.error('DATABASE_URL must be set.');
    process.exit(1);
  }
  const sql = postgres(env.DATABASE_URL, { prepare: false });
  const dir = resolve(process.cwd(), 'supabase', 'migrations');
  const files = readdirSync(dir).filter((f) => f.endsWith('.sql')).sort();
  for (const f of files) {
    const path = join(dir, f);
    console.log(`> ${f}`);
    const text = readFileSync(path, 'utf8');
    await sql.unsafe(text);
  }
  // Seed
  const seed = resolve(process.cwd(), 'supabase', 'seed.sql');
  try {
    const text = readFileSync(seed, 'utf8');
    console.log('> seed.sql');
    await sql.unsafe(text);
  } catch {
    /* no seed file */
  }
  await sql.end({ timeout: 5 });
  console.log('Done.');
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
