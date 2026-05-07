import { resolveAgent, type AgentId } from '@agentboard/shared';

export type ParsedCommand =
  | { kind: 'start' }
  | { kind: 'help' }
  | { kind: 'agents' }
  | { kind: 'ask'; agent: AgentId; message: string }
  | { kind: 'board'; message: string }
  | { kind: 'debate'; message: string }
  | { kind: 'decision'; message: string }
  | { kind: 'task'; agent: AgentId; priority: 'low' | 'medium' | 'high' | 'urgent'; title: string }
  | { kind: 'tasks' }
  | { kind: 'done'; id: string }
  | { kind: 'memory'; note: string }
  | { kind: 'recall'; query: string }
  | { kind: 'brief' }
  | { kind: 'mode'; mode: string }
  | { kind: 'panic'; problem: string }
  | { kind: 'unknown'; raw: string }
  | { kind: 'invalid'; command: string; reason: string };

const PRIORITIES = ['low', 'medium', 'high', 'urgent'] as const;

function rest(text: string, prefix: string): string {
  return text.slice(prefix.length).trim();
}

/**
 * Parse a Telegram message into a structured command. Slash-prefixed only.
 * Returns `null` for non-command messages (free-form text handled by router).
 */
export function parseCommand(input: string): ParsedCommand | null {
  const text = input.trim();
  if (!text.startsWith('/')) return null;

  // strip /command@bot_username when groups force it
  const head = text.split(/\s+/, 1)[0]!;
  const cmd = head.split('@')[0]!.toLowerCase();
  const body = text.slice(head.length).trim();

  switch (cmd) {
    case '/start': return { kind: 'start' };
    case '/help': return { kind: 'help' };
    case '/agents': return { kind: 'agents' };

    case '/ask': {
      const m = body.match(/^(\S+)\s+([\s\S]+)$/);
      if (!m) return { kind: 'invalid', command: 'ask', reason: 'usage: /ask <agent> <message>' };
      const agent = resolveAgent(m[1]!);
      if (!agent) return { kind: 'invalid', command: 'ask', reason: `unknown agent: ${m[1]}` };
      return { kind: 'ask', agent, message: m[2]!.trim() };
    }

    case '/board':
      if (!body) return { kind: 'invalid', command: 'board', reason: 'usage: /board <message>' };
      return { kind: 'board', message: body };

    case '/debate':
      if (!body) return { kind: 'invalid', command: 'debate', reason: 'usage: /debate <message>' };
      return { kind: 'debate', message: body };

    case '/decision':
      if (!body)
        return { kind: 'invalid', command: 'decision', reason: 'usage: /decision <message>' };
      return { kind: 'decision', message: body };

    case '/task': {
      const m = body.match(/^(\S+)\s+(low|medium|high|urgent)\s+([\s\S]+)$/i);
      if (!m)
        return {
          kind: 'invalid',
          command: 'task',
          reason: 'usage: /task <agent> <priority: low|medium|high|urgent> <task>',
        };
      const agent = resolveAgent(m[1]!);
      if (!agent) return { kind: 'invalid', command: 'task', reason: `unknown agent: ${m[1]}` };
      const priority = m[2]!.toLowerCase() as (typeof PRIORITIES)[number];
      return { kind: 'task', agent, priority, title: m[3]!.trim() };
    }

    case '/tasks': return { kind: 'tasks' };

    case '/done': {
      if (!body) return { kind: 'invalid', command: 'done', reason: 'usage: /done <task_id>' };
      return { kind: 'done', id: body.trim() };
    }

    case '/memory':
      if (!body) return { kind: 'invalid', command: 'memory', reason: 'usage: /memory <note>' };
      return { kind: 'memory', note: body };

    case '/recall':
      if (!body) return { kind: 'invalid', command: 'recall', reason: 'usage: /recall <query>' };
      return { kind: 'recall', query: body };

    case '/brief': return { kind: 'brief' };

    case '/mode':
      if (!body) return { kind: 'invalid', command: 'mode', reason: 'usage: /mode <mode>' };
      return { kind: 'mode', mode: body.trim().toLowerCase() };

    case '/panic':
      if (!body) return { kind: 'invalid', command: 'panic', reason: 'usage: /panic <problem>' };
      return { kind: 'panic', problem: body };

    default:
      return { kind: 'unknown', raw: cmd };
  }
}
