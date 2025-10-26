# 🧩 AILO v0.9 — AI Language Object

> **A minimal, safety-first command language where short utterances reconstruct identical intent across humans and machines.**

---

## 🌐 Overview

AILO is a compact, auditable description language for AI systems.
Each statement is an **Action** with typed **Slots** and a **Mood** (`? | . | !`).

| Mood | Meaning          | Side effects                               |
| :--: | :--------------- | :----------------------------------------- |
|  `?` | Query / Ask      | None                                       |
|  `.` | Assert / Report  | Log only                                   |
|  `!` | Commit / Execute | Allowed (⚠ requires `safety rule or risk`) |

Example:

```ailo
act{ag:arm1 obj:potato state:cut size:2cm
    with:{tool:knife} risk:{slip:0.1,burn:0.05}
    rule:safe}! -> check{rule:safe}
```

---

## 🎯 Design Goals

* **Deterministic** → same input ⇒ same plan
* **Explicit** → goals, rules, risks are first-class
* **Compact & Composable** → verbs map to modules
* **Auditable** → machine-verifiable constraints
* **Interoperable** → canonical JSON (CJON) round-trip

---

## 🧱 Core Structure

```
Action := Verb { Slot* } Mood?
Slot   := key : Value
```

Canonical slot order:

`ag, obj, to, state, why, rule, gain, risk, if, when, where, with, limit, cost, conf, src, ref, note, id`

---

## 🧩 Standard Verbs

Core 12 verbs:
`see, want, set, decide, check, learn, map, link, judge, act, recover, end`

Optional extensions include `plan, fetch, filter, verify, notify, move, heat, deploy …`

Each verb has a registered `signature = input → output + side_effects`.

---

## 🔐 Safety Model

* `!` mode requires at least one of `rule | risk | conf`.
* Validator throws `E013 unsafe-commit` otherwise.
* Units and confidence ranges are auto-checked.
* Profiles:

  * `strict` (default)    → safety gates on
  * `lab`                → looser testing
  * `sim`                → no `act!` allowed

---

## 🧮 CJON (JSON Canonical Form)

```json
{
  "verb": "act",
  "mood": "!",
  "slots": {
    "ag": {"id": "robotArm"},
    "obj": {"type": "food", "name": "potato"},
    "state": {"cut": true, "size": {"value": 2, "unit": "cm"}},
    "risk": {"slip": 0.1, "burn": 0.05},
    "conf": 0.88
  },
  "hint": {"then": [{"verb":"check","slots":{"rule":"safe"},"mood":"."}]}
}
```

---

## 🧠 Why AILO?

* **Human-readable like DSL**, yet machine-stable and schema-driven.
* **Language-neutral** bridge between planner, validator, and executor.
* Enables deterministic AI behavior serialization for audit and replay.

---

## 📂 Project Layout

```
/docs/AILO-v0.9-spec.md   # full formal specification
/examples/                # .ailo demo files
/schema/                  # JSON Schema (CJON)
```

---

## ⚖️ License & Version

* **Version:** 0.9 (spec stable, parser beta)
* **License:** MIT (or dual under Hyuna Open Commons 1.0)
* **Compatibility:** forward to AILO 1.0 planned for 2026 Q1

---

## 🚀 Quick Start

```bash
# validate an .ailo file
python ailo_validator.py examples/robot_cut.ailo

# or use CJON
cat examples/robot_cut.json | jq
```

---

## 🤝 Contributing

1. Fork the repo
2. Follow spec rules (section 0–24)
3. Add tests under `/tests/vectors/`
4. Open PR with `spec-compliant` label


---

## 🇰🇷 한글 요약

AILO는 AI 시스템 간의 의미를 **짧고 명확한 언어 구조로 일치시켜 주는 안전 중심 언어**입니다.
각 문장은 `동사 + 슬롯 + 무드` 구조로 이루어져 있으며, 사람이 읽기 쉽고 기계가 검증 가능하도록 설계되었습니다.

```ailo
decide{ag:planner obj://ramen//bibimbap to:meal
       rule:{health:0.6,taste:0.4} why:hurry conf:0.72}! -> act{ag:chef}
```

* `?` → 질문, `.` → 보고, `!` → 실행 (안전 규칙 필수)
* JSON 형태로 완전한 라운드트립 보장
