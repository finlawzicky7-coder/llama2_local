import { z } from 'zod';
import { ALL_AGENT_IDS } from './types.js';

export const AgentIdSchema = z.enum(ALL_AGENT_IDS as [string, ...string[]]);

export const TaskPrioritySchema = z.enum(['low', 'medium', 'high', 'urgent']);
export const TaskStatusSchema = z.enum(['open', 'in_progress', 'blocked', 'done', 'canceled']);

export const MemoryTypeSchema = z.enum([
  'user_preference',
  'business_context',
  'decision',
  'project',
  'task',
  'contact',
  'system_note',
  'lesson_learned',
]);

export const AppModeSchema = z.enum([
  'brainstorm',
  'execute',
  'aggressive',
  'research',
  'investor',
  'builder',
]);

export const CreateTaskInput = z.object({
  agent_id: AgentIdSchema,
  priority: TaskPrioritySchema,
  title: z.string().min(2).max(300),
  description: z.string().max(4000).optional(),
  due_date: z.string().datetime().optional(),
  created_by: z.number().int().optional(),
  source_message_id: z.string().optional(),
});

export const CreateMemoryInput = z.object({
  type: MemoryTypeSchema.default('system_note'),
  content: z.string().min(2).max(8000),
  summary: z.string().max(800).optional(),
  importance_score: z.number().min(0).max(1).default(0.5),
  source: z.string().max(200).optional(),
  expires_at: z.string().datetime().optional(),
  metadata: z.record(z.unknown()).optional(),
});

export const RecallInput = z.object({
  query: z.string().min(1).max(2000),
  top_k: z.number().int().positive().max(20).default(8),
  min_similarity: z.number().min(0).max(1).default(0.5),
});

export const AskCommandInput = z.object({
  agent: AgentIdSchema,
  message: z.string().min(1).max(4000),
});

export const BoardCommandInput = z.object({
  message: z.string().min(1).max(4000),
});

export type CreateTask = z.infer<typeof CreateTaskInput>;
export type CreateMemory = z.infer<typeof CreateMemoryInput>;
export type RecallParams = z.infer<typeof RecallInput>;
