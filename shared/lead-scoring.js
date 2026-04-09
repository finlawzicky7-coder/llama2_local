// Lead scoring rules per funnel. Pure functions, no side effects.
// Score range: 0–100.

/**
 * @typedef {Object} Lead
 * @property {string} name
 * @property {string} email
 * @property {string} [phone]
 * @property {string} [city]
 * @property {number} [budget_or_revenue]
 * @property {string} [service_interest]
 * @property {Object} [raw_payload]
 */

const TARGET_CITIES = new Set([
  'sacramento', 'rocklin', 'roseville', 'elk grove',
  'folsom', 'citrus heights', 'rancho cordova', 'west sacramento'
]);

function normCity(city) {
  return (city || '').trim().toLowerCase();
}

function hasPhone(lead) {
  return !!(lead.phone && lead.phone.replace(/\D/g, '').length >= 10);
}

function inTargetArea(lead) {
  return TARGET_CITIES.has(normCity(lead.city));
}

/** Mid-term rentals (travel nurses) scoring. */
export function scoreMtr(lead) {
  let score = 0;
  const budget = Number(lead.budget_or_revenue) || 0;

  if (budget >= 2800) score += 35;
  else if (budget >= 2000) score += 20;
  else if (budget >= 1200) score += 10;

  if (inTargetArea(lead)) score += 20;
  if (hasPhone(lead)) score += 15;

  const interest = (lead.service_interest || '').toLowerCase();
  if (/travel ?nurse|contract|13 ?week|assignment/.test(interest)) score += 20;
  if (/furnished|month/.test(interest)) score += 10;

  return Math.min(score, 100);
}

/** Cleaning / turnover scoring. */
export function scoreCleaning(lead) {
  let score = 0;
  const revenue = Number(lead.budget_or_revenue) || 0;

  // For cleaning, budget_or_revenue represents jobs-per-month or per-job budget.
  if (revenue >= 400) score += 25;       // multi-unit operator
  else if (revenue >= 150) score += 15;  // single STR
  else if (revenue > 0)    score += 5;

  if (inTargetArea(lead)) score += 25;
  if (hasPhone(lead)) score += 20;

  const interest = (lead.service_interest || '').toLowerCase();
  if (/airbnb|str|short.?term|vrbo|turnover/.test(interest)) score += 20;
  if (/mid.?term|monthly|recurring/.test(interest)) score += 10;

  return Math.min(score, 100);
}

export function scoreLead(lead, funnelSource) {
  switch (funnelSource) {
    case 'mtr':      return scoreMtr(lead);
    case 'cleaning': return scoreCleaning(lead);
    default:         return 0;
  }
}
