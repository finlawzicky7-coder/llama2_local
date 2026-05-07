import { ALL_AGENT_IDS, resolveAgent, type AgentId } from '@agentboard/shared';
import type { AIProvider } from '@agentboard/ai';

export interface RoutingDecision {
  mode: 'single' | 'board' | 'debate' | 'decision' | 'panic' | 'task' | 'memory';
  agents: AgentId[];
  urgency: 'low' | 'normal' | 'high' | 'urgent';
  store_memory: boolean;
  create_task: boolean;
  reason: string;
}

const NAME_RX: Array<[RegExp, AgentId]> = [
  [/\b(atlas|ceo|founder)\b/i, 'ceo'],
  [/\b(forge|cto|engineer|engineering|tech(nical)?)\b/i, 'cto'],
  [/\b(viper|sales|closer|bd)\b/i, 'sales'],
  [/\b(nova|marketing|growth|brand)\b/i, 'marketing'],
  [/\b(ledger|ops|operations|pm)\b/i, 'ops'],
];

const BOARD_RX = /\b(everyone|the board|team|all of you|all agents|whole board|board)\b/i;
const DEBATE_RX = /\b(debate|argue|argument|pros and cons)\b/i;
const DECISION_RX = /\b(decide|make a call|pick one|which one|vote|final answer)\b/i;
const PANIC_RX = /\b(panic|emergency|on fire|broke|broken|down|outage|urgent help)\b/i;
const TASK_RX = /\b(turn (this|that) into tasks|action items|to[\- ]?dos?|next steps)\b/i;
const MEMORY_RX = /\b(remember this|save this|note this|store this)\b/i;
const SELL_RX = /\b(make this sell|how do we sell|sales pitch|conversion|funnel)\b/i;

const URGENT_RX = /\b(asap|now|today|urgent|right now|immediately|critical)\b/i;
const HIGH_RX = /\b(this week|priority|important|soon)\b/i;

/**
 * Rule-based first pass. Returns a high-confidence decision when patterns match,
 * or null when classification needs the LLM fallback.
 */
export function quickRoute(text: string): RoutingDecision | null {
  const t = text.trim();
  if (!t) return null;

  // Memory take-precedence so "remember Atlas said …" doesn't route to CEO.
  if (MEMORY_RX.test(t)) {
    return out('memory', [], 'normal', { store_memory: true, reason: 'memory keyword' });
  }
  if (PANIC_RX.test(t)) {
    return out('panic', ['cto', 'ceo', 'ops'], 'urgent', { reason: 'panic keyword' });
  }
  if (DEBATE_RX.test(t)) {
    return out('debate', [...ALL_AGENT_IDS], urgencyFor(t), { reason: 'debate keyword' });
  }
  if (DECISION_RX.test(t)) {
    return out('decision', [...ALL_AGENT_IDS], urgencyFor(t), { reason: 'decision keyword' });
  }
  if (BOARD_RX.test(t)) {
    return out('board', [...ALL_AGENT_IDS], urgencyFor(t), { reason: 'board keyword' });
  }
  if (TASK_RX.test(t)) {
    return out('single', ['ops'], urgencyFor(t), {
      create_task: true,
      reason: 'tasks keyword → Ops',
    });
  }
  if (SELL_RX.test(t)) {
    return out('board', ['sales', 'marketing'], urgencyFor(t), {
      reason: 'sales+marketing pairing',
    });
  }

  // Direct address ("Atlas, …", "Forge —")
  const addressed = matchAddress(t);
  if (addressed) {
    return out('single', [addressed], urgencyFor(t), {
      reason: `direct address: ${addressed}`,
    });
  }

  // Mention of a single agent name anywhere
  const mentioned = new Set<AgentId>();
  for (const [rx, id] of NAME_RX) {
    if (rx.test(t)) mentioned.add(id);
  }
  if (mentioned.size === 1) {
    const [only] = [...mentioned];
    return out('single', [only!], urgencyFor(t), { reason: 'single mention' });
  }
  if (mentioned.size >= 2) {
    return out('board', [...mentioned], urgencyFor(t), { reason: 'multi-agent mention' });
  }

  return null;
}

function matchAddress(text: string): AgentId | null {
  const m = text.match(/^([A-Za-z]{2,16})[,:\-–—]\s*/);
  if (!m) return null;
  return resolveAgent(m[1]!);
}

function urgencyFor(t: string): RoutingDecision['urgency'] {
  if (URGENT_RX.test(t)) return 'urgent';
  if (HIGH_RX.test(t)) return 'high';
  return 'normal';
}

function out(
  mode: RoutingDecision['mode'],
  agents: AgentId[],
  urgency: RoutingDecision['urgency'],
  rest: Partial<RoutingDecision> & { reason: string },
): RoutingDecision {
  return {
    mode,
    agents,
    urgency,
    store_memory: false,
    create_task: false,
    ...rest,
  };
}

/**
 * LLM fallback — used only when quickRoute returns null. The LLM is asked
 * to emit a single JSON object matching RoutingDecision.
 */
const FALLBACK_SYSTEM = [
  'You are a router for AgentBoard OS.',
  'Decide which orchestration mode to run for the user input.',
  'Modes: single (one agent), board (all 5), debate (3-round), decision (quick call), panic, task (ops should turn into tasks), memory (store note).',
  'Agents: ceo (Atlas), cto (Forge), sales (Viper), marketing (Nova), ops (Ledger).',
  'Reply with ONLY a single JSON object. No prose. No markdown.',
  'Schema: {"mode":"single|board|debate|decision|panic|task|memory","agents":["ceo"|"cto"|"sales"|"marketing"|"ops"],"urgency":"low|normal|high|urgent","store_memory":bool,"create_task":bool,"reason":"<short>"}',
].join('\n');

export async function llmRoute(ai: AIProvider, text: string): Promise<RoutingDecision> {
  const res = await ai.generateText({
    system: FALLBACK_SYSTEM,
    messages: [{ role: 'user', content: text }],
    max_tokens: 200,
    temperature: 0,
  });
  try {
    const parsed = JSON.parse(extractJson(res.text)) as RoutingDecision;
    return normalize(parsed);
  } catch {
    return {
      mode: 'single',
      agents: ['ceo'],
      urgency: 'normal',
      store_memory: false,
      create_task: false,
      reason: 'fallback default',
    };
  }
}

function extractJson(s: string): string {
  const m = s.match(/\{[\s\S]*\}/);
  return m ? m[0] : '{}';
}

function normalize(d: Partial<RoutingDecision>): RoutingDecision {
  const validModes = ['single', 'board', 'debate', 'decision', 'panic', 'task', 'memory'];
  const mode = (validModes.includes(d.mode!) ? d.mode : 'single') as RoutingDecision['mode'];
  const agents = (d.agents ?? []).filter((a): a is AgentId =>
    (ALL_AGENT_IDS as string[]).includes(a),
  );
  return {
    mode,
    agents: agents.length ? agents : ['ceo'],
    urgency: (d.urgency as RoutingDecision['urgency']) ?? 'normal',
    store_memory: Boolean(d.store_memory),
    create_task: Boolean(d.create_task),
    reason: d.reason ?? '',
  };
}

/** Top-level: try fast rule-based first, fall back to LLM if available. */
export async function routeMessage(
  text: string,
  opts: { ai?: AIProvider } = {},
): Promise<RoutingDecision> {
  const quick = quickRoute(text);
  if (quick) return quick;
  if (opts.ai) {
    return llmRoute(opts.ai, text);
  }
  return {
    mode: 'single',
    agents: ['ceo'],
    urgency: 'normal',
    store_memory: false,
    create_task: false,
    reason: 'default → CEO',
  };
}
