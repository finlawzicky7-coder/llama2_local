# Data Model

All tables live in the `public` schema of a Postgres database (Supabase or self-hosted) with the `vector` extension enabled.

## Tables

### `agents`
Seeded with the 5 agents. The bot reads these at boot.

| Column | Type | Notes |
|--------|------|-------|
| id | text PK | `ceo`, `cto`, `sales`, `marketing`, `ops` |
| name | text | "Atlas", "Forge", … |
| role | text | one-line role |
| personality | text | tone description |
| system_prompt | text | full prompt |
| decision_weight | numeric | 0–1 |
| status | text | `active`, `paused` |
| created_at, updated_at | timestamptz |

### `telegram_chats`
| chat_id (bigint PK) | title | type | created_at |

### `telegram_users`
| user_id (bigint PK) | username | first_name | is_admin | created_at |

### `conversations`
A "conversation" is a Telegram chat over time; one row per chat.

| id (uuid) | chat_id | title | mode | last_active_at |

### `messages`
Raw Telegram-side messages (user input + bot replies).

| id (uuid) | chat_id | user_id | role (`user`/`assistant`/`system`) | text | telegram_message_id | created_at |

### `orchestration_runs`
One row per orchestration call.

| id (uuid) | chat_id | user_id | mode | input_text | selected_agents (text[]) | retrieved_memory_ids (uuid[]) | status (`running`/`succeeded`/`partial`/`failed`) | total_tokens | cost_usd | started_at | finished_at | error |

### `agent_responses`
| id | run_id FK | agent_id | round (int) | content | tokens_in | tokens_out | latency_ms | created_at |

### `internal_agent_messages`
Used in debate. Captures the per-agent critique step.

| id | run_id FK | from_agent | to_agent (nullable) | round | content | created_at |

### `tasks`
| id | title | description | agent_id | status | priority | due_date | created_by (telegram user) | source_message_id | dependencies (uuid[]) | progress_notes | created_at | updated_at | completed_at |

### `task_updates`
Audit log of task changes.

| id | task_id FK | field | old_value | new_value | changed_by | created_at |

### `memories`
| id | type | content | summary | embedding (vector(1536)) | source | importance_score | created_at | updated_at | expires_at | metadata jsonb |

Indexed with an IVFFlat cosine index on `embedding`.

### `command_history`
| id | chat_id | user_id | command | args | success | created_at |

### `system_logs`
| id | level (`debug`/`info`/`warn`/`error`) | source | message | metadata jsonb | created_at |

### `api_usage`
| id | provider | model | tokens_in | tokens_out | cost_usd | run_id | created_at |

### `user_permissions`
| user_id PK | role (`admin`/`viewer`) | created_at |

### `app_settings`
Singleton row keyed by `id = 'global'`.

| id | mode | default_model | rate_limit_per_min | updated_at |

## Indexes

- `messages(chat_id, created_at desc)`
- `orchestration_runs(chat_id, started_at desc)`
- `tasks(status, agent_id)`
- `memories` IVFFlat cosine on `embedding`
- `memories(type, importance_score desc)`

## RLS

All tables: enabled. Service role bypasses. Authenticated dashboard users get `select` if `user_permissions.role = 'admin'`.
