# Agent Interaction Map

## Single

```
USER ──▶ <agent> ──▶ reply
```

## Board

```
USER ──▶ Atlas ─┐
        Forge ──┤
        Viper ──┼─▶  Atlas (synthesis) ─▶ Ledger (action plan) ─▶ user
        Nova  ──┤
        Ledger ─┘
```

## Debate

```
Round 1: each agent posts a position
Round 2: each agent critiques the others (writes to internal_agent_messages)
Round 3: each agent posts a refined recommendation
Final:   Atlas decides
Plan:    Ledger executes
```

## Decision

```
USER ──▶ all 5 agents (≤3-bullet quick input)
                 │
                 ▼
              Atlas: choose
                 │
                 ▼
              Ledger: 3 next actions
```

## Panic

```
USER ──▶ Forge (diagnose) ──▶ Atlas (priority P0/P1/P2) ──▶ Ledger (triage)
```

## Brief

```
recent_messages + open_tasks + recent_memories
                 │
                 ▼
       Atlas: decisions/risks/priorities
                 │
                 ▼
       Ledger: top 5 next-24h actions
```

## Decision weights

| Agent  | Weight |
|--------|--------|
| Atlas  | 0.40   |
| Forge  | 0.20   |
| Viper  | 0.15   |
| Nova   | 0.15   |
| Ledger | 0.10   |

Used by future tie-break logic; today every agent's response is preserved verbatim for the user.
