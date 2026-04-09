// Lead router: classify intent, choose the best funnel, assign a score.
// Used by the landing-page capture form and by the n8n webhook-in node
// (n8n Function node: paste this file's contents and call routeLead()).

import { scoreLead } from './lead-scoring.js';

const CLASSIFIERS = [
  {
    funnel: 'mtr',
    match: /travel ?nurse|13 ?week|contract|furnished|mid.?term|month/i,
  },
  {
    funnel: 'cleaning',
    match: /clean|turnover|housekeep|maid|laundry/i,
  },
  {
    funnel: 'cohosting',
    match: /co.?host|manage (my )?airbnb|property manag/i,
  },
  {
    funnel: 'rv',
    match: /rv|motorhome|camper|trailer/i,
  },
];

/**
 * Classify a lead into the best-fit funnel.
 * Priority: explicit funnel_source field > keyword match > fallback.
 */
export function classifyFunnel(lead, explicitSource) {
  if (explicitSource) return explicitSource;

  const haystack = [
    lead.service_interest,
    lead.notes,
    lead.raw_payload && JSON.stringify(lead.raw_payload),
  ].filter(Boolean).join(' ');

  for (const { funnel, match } of CLASSIFIERS) {
    if (match.test(haystack)) return funnel;
  }
  return 'mtr'; // default to the highest-value funnel
}

/**
 * Decide whether to redirect a lead to a better-fit funnel.
 * Example: a cleaning lead with $3k/mo housing budget should also trigger MTR outreach.
 */
export function crossFunnelUpsell(lead, primaryFunnel) {
  const budget = Number(lead.budget_or_revenue) || 0;
  const interest = (lead.service_interest || '').toLowerCase();

  // Cleaning client who owns STRs → co-hosting upsell
  if (primaryFunnel === 'cleaning' && /airbnb|str|vrbo|multiple/.test(interest)) {
    return 'cohosting';
  }

  // MTR searcher with no budget signal but a phone → still route, just lower score
  if (primaryFunnel === 'mtr' && budget === 0 && /clean/.test(interest)) {
    return 'cleaning';
  }

  return null;
}

/**
 * Main entry: returns { funnel_source, lead_score, upsell_funnel }.
 */
export function routeLead(lead, explicitSource) {
  const funnel_source = classifyFunnel(lead, explicitSource);
  const lead_score    = scoreLead(lead, funnel_source);
  const upsell_funnel = crossFunnelUpsell(lead, funnel_source);
  return { funnel_source, lead_score, upsell_funnel };
}
