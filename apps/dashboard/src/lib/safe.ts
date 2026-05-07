/** Wrapper that catches DB errors at render time so the dashboard
 * still loads when the database is offline. */
export async function safe<T>(fn: () => Promise<T>, fallback: T): Promise<T> {
  try {
    return await fn();
  } catch {
    return fallback;
  }
}
