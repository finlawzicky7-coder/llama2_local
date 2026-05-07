import type { AgentId, AgentResponseRecord, Task, TaskPriority } from './types.js';
import { agentLabel } from './agent-aliases.js';

const PRIORITY_ICON: Record<TaskPriority, string> = {
  low: '·',
  medium: '•',
  high: '▲',
  urgent: '!!',
};

export function escapeMarkdown(text: string): string {
  // Telegram MarkdownV2 reserved characters. We use simple Markdown ('Markdown')
  // mode in the bot, but still escape backticks and underscores that would
  // accidentally start/end formatting.
  return text.replace(/([_*`])/g, '\\$1');
}

export function formatAgentResponse(agent: AgentId, content: string): string {
  return `*${agentLabel(agent)}*\n${content.trim()}`;
}

export function formatBoardSummary(args: {
  input: string;
  responses: AgentResponseRecord[];
  synthesis: string;
  action_plan: string;
}): string {
  const blocks = args.responses
    .filter((r) => r.round === 1)
    .map((r) => formatAgentResponse(r.agent_id, r.content));
  return [
    `*Boardroom on:* ${truncate(args.input, 240)}`,
    '',
    blocks.join('\n\n'),
    '',
    `*Final synthesis (Atlas):*\n${args.synthesis.trim()}`,
    '',
    `*Action plan (Ledger):*\n${args.action_plan.trim()}`,
  ].join('\n');
}

export function formatDebateSummary(args: {
  input: string;
  rounds: AgentResponseRecord[];
  final_call: string;
  action_plan: string;
}): string {
  const round1 = args.rounds.filter((r) => r.round === 1);
  return [
    `*Debate on:* ${truncate(args.input, 240)}`,
    '',
    '*Round 1 — Positions:*',
    round1.map((r) => formatAgentResponse(r.agent_id, r.content)).join('\n\n'),
    '',
    `*Final call (Atlas):*\n${args.final_call.trim()}`,
    '',
    `*Execution plan (Ledger):*\n${args.action_plan.trim()}`,
  ].join('\n');
}

export function formatDecisionSummary(args: {
  input: string;
  inputs: AgentResponseRecord[];
  decision: string;
  next_actions: string;
}): string {
  return [
    `*Decision needed:* ${truncate(args.input, 240)}`,
    '',
    args.inputs.map((r) => formatAgentResponse(r.agent_id, r.content)).join('\n\n'),
    '',
    `*Decision (Atlas):*\n${args.decision.trim()}`,
    '',
    `*Next actions (Ledger):*\n${args.next_actions.trim()}`,
  ].join('\n');
}

export function formatTaskList(tasks: Task[]): string {
  if (!tasks.length) return '_No open tasks._';
  return tasks
    .map((t) => {
      const icon = PRIORITY_ICON[t.priority];
      const due = t.due_date ? `  · due ${t.due_date.slice(0, 10)}` : '';
      return `${icon} *#${shortId(t.id)}* — ${t.title}  _(${t.agent_id} · ${t.status})_${due}`;
    })
    .join('\n');
}

export function formatTaskCreated(task: Task, dashboardUrl?: string): string {
  const dash = dashboardUrl ? `\n${dashboardUrl}/tasks/${task.id}` : '';
  return [
    `*Task created* — #${shortId(task.id)}`,
    `_${task.priority.toUpperCase()}_  ·  owner: *${task.agent_id}*  ·  status: ${task.status}`,
    '',
    task.title,
    task.description ? `\n${task.description}` : '',
    dash,
  ].join('\n');
}

export function shortId(id: string): string {
  return id.replace(/-/g, '').slice(0, 8);
}

export function truncate(s: string, n: number): string {
  if (s.length <= n) return s;
  return s.slice(0, n - 1).trimEnd() + '…';
}
