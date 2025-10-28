# TSX v0.1 — Intent Projection Language (Full Spec)

> **Purpose**
> TSX (Intent Projection Language) is a compact, auditable layer that turns *thinking/intent* into safe, executable **plans**. It is designed to compile deterministically into **AILO** actions, without exposing private upstream languages.

---

## 0. Design Goals

* **Deterministic**: same input → same parse → same projection.
* **Separable**: intent (TSX) ≠ action (AILO). TSX never acts by itself.
* **Compact**: minimal surface, dense semantics.
* **Auditable**: first‑class goals, constraints, risks, evidence.
* **Interoperable**: canonical JSON (CJON), round‑trip from text.
* **Transpilable**: one‑shot, rule‑based mapping → AILO.

---

## 1. Core Model

A TSX statement is an **Intent** with **Slots** and an optional **Mode**.

```
Intent := Verb { Slot* } Mode?
Slot   := key : Value
Mode   := ? | ! | .
```

* `?` = *inquire/plan* (no side‑effects)
* `!` = *project/commit* (authorizes projection to AILO; TSX itself has no world effects)
* `.` = *assert/report* (log only)
* Default mode is `.` if omitted.

### 1.1 Canonical Slot Order (stable hashing)

`who, target, goal, strategy, prefs, avoid, tradeoff, rule, risk, accept, evidence, conf, if, when, where, with, budget, cost, privacy, src, ref, note, id`

> Unknown keys allowed; they serialize **after** the known set.

### 1.2 Minimal Surface

* Braces `{}` for comma‑separated slots, e.g., `plan{who:a,target:b}`
* Arrays `[]`, sets `|…|`, tuples `(…)`, maps `{k:v}` inside values
* Choice: `//alt1//alt2//`
* Sequence: `;` between statements (newline ≡ `;`)
* Projection hint: trailing `-> ailo{…}` is *advisory* (not required)

---

## 2. Data & Types

**Scalars**: `int`, `float`, `bool`, `str`, `time`, `duration`, `percent(0..1)`, `uid`

**Literals**

* Numbers: `42`, `3.14`, `1e-9`
* Percent in [0,1]: `conf:0.72`, `risk:{overrun:0.1}`
* Strings: double‑quoted if spaces (`"high priority"`), otherwise bare identifiers
* Time: ISO‑8601 (`2025-10-28T09:00+09:00`), date (`2025-10-28`)
* Duration: `5m`, `2h30m`, `1.2s`
* Quantities with units: `2cm`, `3kg`, `90C`, `60%` (internally normalized)

**Thing** (open record): `thing{type:doc, topic:"safety"}`

---

## 3. Reserved Slot Keys

* `who` — agent or role issuing the intent
* `target` — object/focus of the intent (thing or set)
* `goal` — desired outcome/state (natural language or structured)
* `strategy` — approach, method, or constraints on procedure
* `prefs` — weighted preferences `{quality:0.6, speed:0.4}`
* `avoid` — disallowed states/resources `{tools:["x"], topics:[…]}`
* `tradeoff` — explicit trade rules, e.g. `quality>speed`
* `rule` — hard policy name(s) or logical constraints `all(…)`
* `risk` — hazards with probabilities `{leak:0.01}`
* `accept` — acceptable risk budget/level `{max:0.05}`
* `evidence` — prior facts/links justifying the intent
* `conf` — self‑confidence (0..1)
* `if` — preconditions/guards
* `when` — time window or schedule
* `where` — location/context label
* `with` — available resources/tools/capabilities
* `budget` — time/cost/tries `{time:10m, cost:"$5", tries:2}`
* `cost` — expected cost
* `privacy` — data handling hints `{pii:false}`
* `src` — data sources (URIs/labels)
* `ref` — external IDs
* `note` — human note
* `id` — stable statement id

> Semantics are order‑independent; canonical order is for hashing and diffs.

---

## 4. Standard Verbs (TSX v0.1)

Core (no side‑effects): `plan, ask, compare, evaluate, justify, scope, refine`
Projection verbs (authorize AILO emission when `!`): `project, schedule, allocate`

**Examples**

* `ask{target:dataset rule:licensed}?`
* `plan{who:analyst target://report//dashboard// goal:insight prefs:{quality:0.7,speed:0.3}}.`
* `project{who:orchestrator target:harvest goal:news-brief rule:{all(safe,licensed)} risk:{hallucination:0.05} conf:0.9}!`

---

## 5. Rules & Conditions

**Rule** forms

* Inequality: `quality>speed`, `temp<=90C`, `time<10m`
* Weighted set: `{quality:0.6, speed:0.4}`
* Policy name(s): `rule:safe`, `rule:GDPR`
* Logic: `all( … )`, `any( … )`, `not( … )`

**Condition** forms

* Resource/state: `battery>0.2`, `exists(with.tool:knife)`
* Event: `cond:deadline.reached==false`

---

## 6. Operators & Sugar

* `=` bind/define literal; `==` compare (in `rule`/`if`)
* `~` approximate literal, e.g. `~2h`
* Choice: `//A//B//` (resolve by `refine/compare` or downstream policy)
* Pipeline macro (reader): `expr |> verb{…}` expands with a temp id

---

## 7. Modes & Safety

* `?` plan/inquire only; must not yield executable AILO
* `.` assert/report only; may log to trace
* `!` *projection commit*: authorizes deterministic **AILO** emission
  **Barrier**: `!` requires at least **one** of `{rule, risk, conf}` else validator error `E013` (unsafe‑projection)

---

## 8. Error Model (Validator)

* `E001: parse-fail`
* `E002: unknown-verb`
* `E003: slot-type-mismatch`
* `E004: missing-required-slot`
* `E005: bad-unit`
* `E006: rule-unsatisfied`
* `E007: cond-unsatisfied`
* `E010: mode-forbidden`
* `E013: unsafe-projection`
* `E020: overflow/underflow`

Each error includes `loc, hint, expected, got`.

---

## 9. Canonical JSON (CJON)

Round‑trip, lossless.

```json
{
  "verb": "project",
  "mode": "!",
  "slots": {
    "who": {"id": "orchestrator"},
    "target": {"type": "harvest", "topic": "news"},
    "goal": "news-brief",
    "rule": ["safe", "licensed"],
    "risk": {"hallucination": 0.05},
    "conf": 0.9,
    "budget": {"time": "5m"}
  },
  "hint": {"then": [{"verb":"evaluate","mode":".","slots":{"prefs":{"accuracy":0.7,"coverage":0.3}}}]}
}
```

---

## 10. EBNF Grammar (Surface)

```
program   = { stmt, sep };
sep       = ";" | NEWLINE;
stmt      = intent, [ws], [result];
intent    = verb, [ws], obj;
verb      = ident;
obj       = "{" , [slot, { "," , slot } ] , "}", [mode];
slot      = key, ":", value;
key       = ident;
value     = scalar | record | array | set | tuple | choice | rulex | logic;
scalar    = number | string | ident | time | duration | quantity;
record    = ident, "{", [pair, {",", pair}], "}";
pair      = ident, ":", value;
array     = "[", [value, {",", value}], "]";
set       = "|", [value, {",", value}], "|";
tuple     = "(", [value, {",", value}], ")";
choice    = "//", value, {"//", value}, "//";
rulex     = ident, ("<"|"<="|">"|">="|"=="), value;
logic     = ident, "(", [value, {",", value}], ")";
mode      = "?" | "!" | ".";
ident     = /[A-Za-z_][A-Za-z0-9_]*+/;
number    = /[-+]?(?:\d+\.\d+|\d+)(?:[eE][-+]?\d+)?/;
string    = '"' (ESC|.)* '"';
quantity  = number, unit;      unit = /[A-Za-z%°]+/;
duration  = /\d+(?:\.\d+)?[smhdw](?:\d+(?:\.\d+)?[smhdw])*/;
time      = /\d{4}-\d{2}-\d{2}(?:T[^\s]+)?/;
ws        = /[ \t]+/;
```

---

## 11. Validation Rules

1. Verb must exist in registry; else `E002`.
2. Slot typing per verb signature; unknown keys allowed unless verb forbids.
3. `!` requires ≥1 of `{rule, risk, conf}`; else `E013`.
4. `when` is `Time | {start:Time, end:Time}` with `end>start`.
5. Units auto‑convert; incompatible units → `E005`.
6. `conf ∈ [0,1]`; each `risk.k ∈ [0,1]`.
7. Choice `//…//` must be resolved before projection to AILO.

---

## 12. Projection Interface (TSX → AILO)

**Deterministic mapping table**

| TSX slot   | AILO slot                   |
| ---------- | --------------------------- |
| `who`      | `ag`                        |
| `target`   | `obj`                       |
| `goal`     | `to`                        |
| `strategy` | `state` (or verb‑specific)  |
| `prefs`    | `rule` weighted set         |
| `avoid`    | `rule` negative constraints |
| `tradeoff` | `rule` inequality           |
| `rule`     | `rule`                      |
| `risk`     | `risk`                      |
| `accept`   | `limit`/policy              |
| `when`     | `when`                      |
| `where`    | `where`                     |
| `with`     | `with`                      |
| `budget`   | `limit`                     |
| `cost`     | `cost`                      |
| `conf`     | `conf`                      |
| `src`      | `src`                       |
| `ref`      | `ref`                       |
| `note`     | `note`                      |

**Projection verbs → AILO verbs**

* `project{…}!` → choose target AILO verb by `goal/strategy` (resolver table)
  default: `act{…}!` if `state/strategy` implies world action, else `see/check/decide`.
* `schedule{…}!` → `reserve/notify` + time‑boxed `act` plan
* `allocate{…}!` → `reserve{with:{…} limit:{…}}!`

**Resolver table (starter)**

* `goal:research | target:harvest/news` → `fetch`/`see` (+ `filter/group/summarize` as hints)
* `goal:report` → `map`/`explain`/`notify`
* `goal:execute` with `strategy:{tool:*}` → `act`

**Projection record** (audit)

```json
{
  "tsx": { /* CJON intent */ },
  "ailo": [{ /* emitted AILO CJON(s) */ }],
  "trace": {"ts":"2025-10-28T03:00:00Z","policy":"strict"}
}
```

---

## 13. Security & Policy Hooks

* Verbs carry `safety_level ∈ {plan, act}`; TSX runtime enforces no external effects.
* Capability tokens required at projection (`with:{caps:[…]}`) for high‑risk goals.
* Compliance profiles: `strict` (projection requires `rule|risk|conf`), `lab` (warn), `sim` (no projection).

---

## 14. Style & Linting

* Prefer explicit `who, target, goal`.
* Keep `conf`, `risk` when committing.
* Use named policies: `rule:safe`, `rule:orgPolicyX`.
* Provide human `note` for ops handoff.

---

## 15. Worked Examples

**A. Web research plan → projection**

```
plan{who:analyst target:news goal:brief prefs:{accuracy:0.7,speed:0.3} rule:safe}?  
project{who:analyst target:news goal:brief rule:{all(safe,licensed)} risk:{hallucination:0.05} conf:0.9 budget:{time:5m}}!
```

→ Projection (illustrative):

```
fetch{obj:news rule:licensed}?; filter{rule:date>=2025-10-01}.; map{rule:summarize(5 bullets)}.; notify{to:"#research"}!
```

**B. Robot cut with safety (high level → action)**

```
project{who:arm1 target:potato goal:sliced strategy:{cut:true,size:2cm} rule:safe risk:{slip:0.1,burn:0.05} with:{tool:knife} when:{start:2025-10-28T09:00+09:00}}!
```

→ AILO:

```
act{ag:arm1 obj:potato state:cut size:2cm with:{tool:knife} risk:{slip:0.1,burn:0.05} rule:safe when:{start:2025-10-28T09:00+09:00}}! -> check{rule:safe}
```

**C. Data pipeline intent**

```
plan{who:etl target:"s3://bucket/x.csv" goal:refresh prefs:{freshness:0.6,cost:0.4}}.
project{who:etl target:"s3://bucket/x.csv" goal:refresh rule:safe budget:{time:10m}}!
```

→ AILO:

```
fetch{src:"s3://bucket/x.csv"}?; filter{rule:age<10m}.; group{rule:by(country)}.; notify{to:"#ops" note:"refresh ok"}!
```

---

## 16. Verb Signatures (excerpt)

* `plan(target, goal, prefs?, rule?, risk?, conf?) -> Plan, sidefx:none`
* `ask(target, rule?) -> Answer, sidefx:none`
* `compare(options, prefs) -> Choice, sidefx:none`
* `evaluate(thing, rule|prefs) -> score∈[0,1], sidefx:none`
* `refine(plan, feedback) -> Plan, sidefx:none`
* `project(intent) -> AILO-CJON[], sidefx:emit`
* `schedule(intent, when) -> AILO-CJON[], sidefx:emit`
* `allocate(resources, budget) -> AILO-CJON[], sidefx:emit`

---

## 17. Test Vectors

1. `plan{target:news goal:brief}?` ✅
2. `compare{target://a//b// prefs:{x:0.7,y:0.3}}.` ✅
3. `project{who:arm target:potato}!` ❌ `E013` (missing safety)
4. `project{who:arm target:potato strategy:{size:2sm}}!` ❌ `E005` (unit)

---

## 18. CJON Schema (JSON Schema draft‑07)

```json
{
  "$schema":"http://json-schema.org/draft-07/schema#",
  "title":"TSX Intent",
  "type":"object",
  "required":["verb","slots"],
  "properties":{
    "verb":{"type":"string"},
    "mode":{"enum":["?","!","."]},
    "slots":{"type":"object"},
    "hint":{"type":"object"}
  },
  "additionalProperties":false
}
```

---

## 19. Versioning & Profiles

* Header (optional): `#! TSX 0.1 profile:strict` at file start
* Profiles: `strict` (safety gates on), `lab` (looser), `sim` (no projection)

---

## 20. Quick Cheat Sheet

```
VERB{who:_, target:_, goal:_, strategy:_, prefs:_, avoid:_, tradeoff:_, rule:_, risk:_, accept:_, evidence:_, conf:_, if:_, when:_, where:_, with:_, budget:_, cost:_, privacy:_, src:_, ref:_, note:_} MODE
```

* `?` plan, `.` tell, `!` project
* `//a//b//` choose, `~` approx
* Always add `rule` or `risk` (or `conf`) before `!`

---

### End of TSX v0.1
