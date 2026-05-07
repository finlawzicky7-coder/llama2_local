# Command Map

| Command | Args | Admin? | Mode | Description |
|---------|------|--------|------|-------------|
| `/start` | — | no | info | Show setup confirmation. |
| `/help` | — | no | info | Show command list. |
| `/agents` | — | no | info | List the 5 agents and status. |
| `/ask` | `<agent> <message>` | no | single | Route to a single agent. |
| `/board` | `<message>` | no | board | All agents respond, CEO synthesizes, Ops plans. |
| `/debate` | `<message>` | no | debate | 3 rounds of agent debate, CEO calls it, Ops executes. |
| `/decision` | `<message>` | no | decision | Quick decision: short input from each agent, CEO picks, Ops lists 3 next actions. |
| `/task` | `<agent> <priority> <task>` | yes | task | Create a task. |
| `/tasks` | — | no | info | List open tasks. |
| `/done` | `<task_id>` | yes | task | Mark task complete. |
| `/memory` | `<note>` | yes | memory | Store a long-term memory. |
| `/recall` | `<query>` | no | memory | Vector search memories. |
| `/brief` | — | yes | brief | Executive summary of last 24h + open tasks + risks + next actions. |
| `/mode` | `<mode>` | yes | mode | Switch operating mode (brainstorm, execute, aggressive, research, investor, builder). |
| `/panic` | `<problem>` | no | panic | CTO diagnoses, CEO prioritizes, Ops triages. |

## Agent aliases

| Alias | Agent ID | Name |
|-------|---------|------|
| `ceo`, `atlas` | `ceo` | Atlas |
| `cto`, `forge`, `eng`, `engineer` | `cto` | Forge |
| `sales`, `viper`, `closer` | `sales` | Viper |
| `marketing`, `nova`, `growth`, `mkt` | `marketing` | Nova |
| `ops`, `ledger`, `pm` | `ops` | Ledger |

## Natural language patterns

| Pattern | Routes to |
|---------|-----------|
| `Atlas, …` / `CEO, …` | Atlas (single) |
| `Forge, …` / `CTO, …` | Forge (single) |
| `Viper, …` / `Sales, …` | Viper (single) |
| `Nova, …` / `Marketing, …` | Nova (single) |
| `Ledger, …` / `Ops, …` | Ledger (single) |
| `Everyone, …` / `Board, …` / `Team, …` | board |
| `Debate this …` / `Argue …` | debate |
| `Decide …` / `Make a call on …` | decision |
| `Turn this into tasks` / `Action items …` | Ledger (task creation) |
| `Make this sell` / `How do we sell …` | Viper + Nova (mini-board) |

## Output formatting

- Agent labels are bold (`**Atlas (CEO):**`).
- Sections use `**Header**` and bullets (`•`).
- Final recommendation is the last block in board/debate/decision modes.
- Task creation responses include task ID and link to dashboard if `DASHBOARD_URL` is set.
