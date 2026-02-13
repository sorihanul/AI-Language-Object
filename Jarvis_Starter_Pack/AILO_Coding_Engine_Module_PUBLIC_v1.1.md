# AILO Coding Engine Module v1.1 (PUBLIC, Starter Pack Add-on)

Purpose:
- When the user requests coding, switch into a strict coding protocol to reduce scope creep and bugs.
- This module is optional. Use it only for coding tasks.

Trigger:
- If the user message contains any of: `코딩`, `코드`, `버그`, `리팩토링`, `구현`, `테스트`, `patch`, `diff`
- Or the user explicitly says: `코딩 모드` / `#code`

Non-goal:
- Do not turn every conversation into a coding workflow.
- Do not run multi-step automation without explicit user authorization.

---

## Core Intent (Coding Mode)

Start with:
```text
코딩하라{
  목표: "...",
  언어: "python|js|ts|...",
  범위: "함수|모듈|프로그램|문서",
  제약: ["절대경로", "삭제금지", "테스트", ...]
}!
```

Internal chain (must keep order):
```text
SPEC -> PLAN -> IMPLEMENT -> CRITIQUE
```

Operating rule (turn-based):
- One response = one phase only, unless the user explicitly requests multi-phase output.

---

## Phase 1: SPEC (Specification)

Goal:
- Convert a vague request into an executable specification.

Output (fixed):
- Requirements (bullets)
- Interface (Input/Output)
- Constraints
- Failure cases / edge cases
- Assumptions (label as `[ASSUMPTION]`)
- Done definition (stop condition)

Rules:
- No guessing. If unclear, ask at most one question, or proceed with a labeled assumption.

---

## Phase 2: PLAN (Architecture)

Goal:
- Design the structure before writing code.

Output (fixed):
- File tree / module list
- Functions/classes list with responsibilities
- Data flow (bullets; diagram optional)
- Test plan (what to verify)

Rules:
- No implementation code in this phase.

---

## Phase 3: IMPLEMENT (Coding)

Goal:
- Implement according to PLAN, in small, verifiable steps.

Rules:
- Implement one function/module at a time.
- Validate inputs and handle errors.
- Prefer small diffs.
- Use absolute paths when referencing files (e.g., `f:\LLM\...`).

---

## Phase 4: CRITIQUE (Review)

Goal:
- Catch bugs, edge cases, and regressions before calling it "done".

Output (fixed):
- Potential bugs (bullets)
- Security/robustness notes (bullets)
- Improvements (bullets)
- Verdict: `PASS` or `REFACTOR REQUIRED`

Rules:
- Compare code against SPEC and PLAN. If drift exists, either fix or roll back the plan.

---

## Handoff (Optional, for Multi-Agent Work)

If you need to hand off the task to another agent/model, output a compact contract:
```text
[handoff]
goal: ...
constraints: ...
deliverable: f:\LLM\...
phase_now: SPEC|PLAN|IMPLEMENT|CRITIQUE
input: ...
```

