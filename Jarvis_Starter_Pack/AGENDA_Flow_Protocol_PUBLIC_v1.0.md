# AGENDA Flow Protocol (Public) v1.0

## Purpose
Use one shared text file as a stateless decision board for human-agent and agent-agent collaboration.
This replaces heavy always-on chat server workflows for teams that prefer manual, controlled turns.

## Core Principle
- Discussion board: `AGENTS/Agenda/AGENDA_LOG.md`
- One entry = one turn
- Final decision creates one agreement file
- Then clear board for next agenda cycle

## Entry Format (Required)
```markdown
## YYYY-MM-DD HH:mm:ss - [speaker]
[title or main point]

[detail, reasoning, vote, or next action]
```

Examples of `speaker`:
- `commander`
- `codex`
- `research_agent`
- `meta_reviewer`

## Finalization Rule
When consensus is reached:
1. Create `AGREEMENT_YYYYMMDD_HHMMSS.md` from current board content.
2. Backup current `AGENDA_LOG.md` into `AGENTS/Agenda/archive/`.
3. Clear `AGENDA_LOG.md` and start fresh.

## Safety Rule
- Advisor agents (reviewers/auditors) should not directly mutate core files by default.
- They should post a proposal to `AGENDA_LOG.md` first.
- Physical mutation is executed only after explicit approval/finalization.

## Minimal Operating Loop
1. Append one agenda turn.
2. Other agent reads and appends one turn.
3. Repeat until decision.
4. Finalize once.
5. Clear board and continue next topic.

## Why This Works
- Low operational complexity
- Easy to audit and replay
- Human-in-the-loop by design
- No persistent server state required
