export type AgentId = 'ceo' | 'cto' | 'sales' | 'marketing' | 'ops';

export const ALL_AGENT_IDS: AgentId[] = ['ceo', 'cto', 'sales', 'marketing', 'ops'];

export type OrchestrationMode =
  | 'single'
  | 'board'
  | 'debate'
  | 'decision'
  | 'panic'
  | 'brief'
  | 'task'
  | 'memory';

export type TaskStatus = 'open' | 'in_progress' | 'blocked' | 'done' | 'canceled';
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';

export type MemoryType =
  | 'user_preference'
  | 'business_context'
  | 'decision'
  | 'project'
  | 'task'
  | 'contact'
  | 'system_note'
  | 'lesson_learned';

export type AppMode =
  | 'brainstorm'
  | 'execute'
  | 'aggressive'
  | 'research'
  | 'investor'
  | 'builder';

export interface AgentResponseRecord {
  agent_id: AgentId;
  round: number;
  content: string;
  tokens_in: number;
  tokens_out: number;
  latency_ms: number;
}

export interface Task {
  id: string;
  title: string;
  description: string | null;
  agent_id: AgentId;
  status: TaskStatus;
  priority: TaskPriority;
  due_date: string | null;
  created_by: number | null;
  source_message_id: string | null;
  dependencies: string[];
  progress_notes: string | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

export interface Memory {
  id: string;
  type: MemoryType;
  content: string;
  summary: string | null;
  importance_score: number;
  source: string | null;
  created_at: string;
  updated_at: string;
  expires_at: string | null;
  metadata: Record<string, unknown>;
}

export interface OrchestrationRun {
  id: string;
  chat_id: number | null;
  user_id: number | null;
  mode: OrchestrationMode;
  input_text: string;
  selected_agents: AgentId[];
  retrieved_memory_ids: string[];
  status: 'running' | 'succeeded' | 'partial' | 'failed';
  total_tokens: number;
  cost_usd: number;
  started_at: string;
  finished_at: string | null;
  error: string | null;
}
