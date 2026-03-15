// Simple unique ID generator (no external library needed)
export function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 9);
}

// localStorage keys
const CONTACTS_KEY = 'simpleCRM_contacts';
const CALLS_KEY = 'simpleCRM_calls';

// Load data from localStorage, returning a default if nothing is stored
export function loadContacts() {
  try {
    const data = localStorage.getItem(CONTACTS_KEY);
    return data ? JSON.parse(data) : [];
  } catch {
    return [];
  }
}

export function saveContacts(contacts) {
  localStorage.setItem(CONTACTS_KEY, JSON.stringify(contacts));
}

export function loadCalls() {
  try {
    const data = localStorage.getItem(CALLS_KEY);
    return data ? JSON.parse(data) : [];
  } catch {
    return [];
  }
}

export function saveCalls(calls) {
  localStorage.setItem(CALLS_KEY, JSON.stringify(calls));
}

// Date helpers
export function todayString() {
  return new Date().toISOString().split('T')[0]; // "YYYY-MM-DD"
}

export function addDays(dateStr, days) {
  const d = new Date(dateStr);
  d.setDate(d.getDate() + days);
  return d.toISOString().split('T')[0];
}

export function formatDate(dateStr) {
  if (!dateStr) return '—';
  const d = new Date(dateStr + 'T00:00:00'); // avoid timezone shift
  return d.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

export function daysDiff(dateStr) {
  const today = new Date(todayString() + 'T00:00:00');
  const target = new Date(dateStr + 'T00:00:00');
  return Math.round((target - today) / (1000 * 60 * 60 * 24));
}
