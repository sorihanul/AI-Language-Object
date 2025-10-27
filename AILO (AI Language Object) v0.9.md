# AILO (AI Language Object) v0.9 — Full Specification

> Purpose: A minimal, safety‑first command/description language for AI systems where **short utterances reconstruct the same state** across humans and machines.

---

## 0. Design Goals

- **Determinism**: Same input → same parse → same plan.
    
- **Explicitness**: Goals, rules, evidence, uncertainty, risks are first‑class.
    
- **Compactness**: Write less without losing semantics.
    
- **Composable**: Slot grammar; verbs map to modules.
    
- **Auditable**: Machine‑verifiable constraints; human‑readable.
    
- **Interoperable**: Canonical JSON; round‑trip formatting.
    

---

## 1. Core Model

An AILO statement is an **Action** with **Slots** and optional **Mood**.

```
Action := Verb { Slot* } Mood?
Slot   := key : Value
Mood   := ? | ! | .
```

- `?` = query/ask, no side‑effects
    
- `!` = commit/execute, side‑effects allowed
    
- `.` = assert/report, side‑effects forbidden
    
- Default mood is `.` if omitted.
    

### 1.1 Canonical Order (for stable diffs)

`ag, obj, to, state, why, rule, gain, risk, if, when, where, with, limit, cost, conf, src, ref, note, id` (unknown keys allowed but come after these).

### 1.2 Minimal Surface

- Braces `{}` hold comma‑separated slots: `verb{ag:a,obj:b}`
    
- Arrays `[]`, sets `|…|`, tuples `(…)`, maps `{k:v}` inside values
    
- Multi‑alternative **choice**: `//alt1//alt2//`
    
- Sequence: `;` between statements (line break ≡ `;`)
    
- Arrow result hint: `->` trailing predictive effect(s)
    

---

## 2. Data & Types

**Scalars**: `int`, `float`, `bool`, `str`, `time`, `duration`, `percent(0..1)`, `uid`

**Structures**: `Thing`, `Rule`, `Feat`, `Reason`, `Place`, `Time`, `Cond`, `Plan`, `Measure`, `Trace` (open records)

**Literals**

- Numbers: `42`, `3.14`, `1e-9`
    
- Percent in [0,1]: `conf:0.72`, `risk:{burn:0.05}`
    
- Strings: double quotes for spaces: `"hot potato"`; bare words for identifiers: `robotArm`
    
- Time: ISO‑8601 (`2025-10-25T09:00+09:00`), date (`2025-10-25`)
    
- Duration: `5m`, `2h30m`, `1.2s`
    
- Units (quantity): `2cm`, `3kg`, `120C`, `60%` (converted to canonical SI internally; `%` → `percent`)
    

**Thing**: open record with `type` and features, e.g. `food{hot:true, spice:0.6}`

---

## 3. Reserved Slot Keys

- `ag` (Agent) – who acts
    
- `obj` (Object/Target)
    
- `to` (Goal) – objective or desired state
    
- `state` (Feature/Mode) – how to act or resulting state
    
- `why` (Reason/Evidence)
    
- `rule` (Constraints/Policy) – hard or soft rules
    
- `gain` (Expected benefit)
    
- `risk` (Hazards with probabilities)
    
- `if` (Precondition/Guard)
    
- `when` (Time window/schedule)
    
- `where` (Location/Context)
    
- `with` (Resources/Tools)
    
- `limit` (Budgets: time, cost, tries)
    
- `cost` (Estimated cost)
    
- `conf` (Confidence 0..1)
    
- `src` (Data sources)
    
- `ref` (References/IDs)
    
- `note` (Human note)
    
- `id` (Stable statement id)
    

> Slots are **unordered semantically** but must serialize canonically.

---

## 4. Verbs (Standard Library v0.9)

**Core 12**: `see, want, set, decide, check, learn, map, link, judge, act, recover, end`

**Extended** (optional): `plan, fetch, filter, sort, group, sample, infer, explain, verify, log, notify, reserve, move, grasp, cut, heat, cool, mix, assemble, deploy, rollback`

> New verbs MUST register `signature = input→output + side_effects` in module registry.

**Examples**

- `see{obj:fridge rule:inventory}?`
    
- `decide{to:meal obj://ramen//bibimbap rule:{health>taste weight:0.6} why:hurry conf:0.72}!`
    
- `act{ag:robot obj:potato state:cut size:2cm risk:{slip:0.1,burn:0.05}}! -> check{rule:safe}`
    

---

## 5. Rules & Conditions

**Rule** literal forms:

- Inequality: `health>taste`, `temp<=90C`, `time<10m`
    
- Weighted set: `{health:0.6, taste:0.4}`
    
- Policy name: `rule:HIPAA`, `rule:safe`
    
- Logic: `all( … )`, `any( … )`, `not( … )`
    

**Cond** forms:

- Sensor/event: `cond:door.open==true`
    
- Resource: `battery>0.2`
    
- Existential: `exists(obj:knife)`
    

---

## 6. Operators & Syntax Sugar

- Equality: `=` (bind/define), `==` (compare in `rule`/`if`)
    
- Approx: `~` (approximate literal), e.g. `~2m`
    
- Choice: `//A//B//`
    
- Pipeline: `expr |> verb{…}` (reader macro expands to temp id)
    
- Template param: `$name` inside values (macro arguments)
    

---

## 7. Moody Semantics

- `?` **Query**: may read; must not write; planner returns `Answer`
    
- `.` **Assert/Report**: write only to log/trace; no external effect
    
- `!` **Commit**: execute plan; must emit `Trace` + `Outcome`
    

**Safety Barrier**: `!` requires `risk` OR `rule` present (configurable), else validator error `E013: unsafe-commit`.

---

## 8. Error Model (Validator)

- `E001: parse-fail`
    
- `E002: unknown-verb`
    
- `E003: slot-type-mismatch`
    
- `E004: missing-required-slot`
    
- `E005: bad-unit`
    
- `E006: rule-unsatisfied`
    
- `E007: cond-unsatisfied`
    
- `E010: mood-forbidden` (e.g., `learn!` in read-only context)
    
- `E013: unsafe-commit`
    
- `E020: overflow/underflow`
    

Each error includes `loc`, `hint`, `expected`, `got`.

---

## 9. Canonical JSON (CJON)

Round‑trip, lossless representation.

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

## 10. EBNF Grammar (Surface)

```
program   = { stmt, sep };
sep       = ";" | NEWLINE;
stmt      = action, [ws], [result];
action    = verb, [ws], obj;
verb      = ident;
obj       = "{" , [slot, { "," , slot } ] , "}", [mood];
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
mood      = "?" | "!" | ".";
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

1. **Verb known** or present in registry; else `E002`.
    
2. **Slot typing** per verb signature; unknown keys allowed unless verb forbids.
    
3. `!` requires at least one of `{rule, risk, conf}`; configurable.
    
4. Time windows: `when` must be `Time | {start:Time, end:Time}`; end>start.
    
5. Units auto‑convert; incompatible units → `E005`.
    
6. `conf∈[0,1]`; each `risk.k ∈ [0,1]`.
    
7. Choice `//…//` resolves by `decide` or downstream policy; not directly executable.
    

---

## 12. Planning & Execution Interface

- **Registry**: `verb → module(signature, effects, safety_level)`
    
- **Planner I/O**
    
    - In: CJON action(s)
        
    - Out (Query `?`): `{answer:any, conf, trace}`
        
    - Out (Commit `!`): `{outcome, conf, trace, errors?}`
        
- **Trace** (append‑only): `ts, agent, action, inputs, outputs, env, risks, rulesChecked`
    

---

## 13. Macros & Templates (v0.9‑exp)

- Define: `set{name:$x value:$v}` inside `macro name($x,$v)= …` file‑level.
    
- Use: `@name(timer,300s)` expands before parse.
    
- Hygiene: macro can only emit valid AILO; no token pasting.
    

---

## 14. Interop & Serialization

- File: `.ailo` (UTF‑8). One statement per line; `#` line comments.
    
- Canonical order + minimal whitespace for hashing.
    
- Lossless round‑trip to CJON; pretty‑printer optional.
    

---

## 15. Security & Policy Hooks

- **Sandbox**: verbs carry `safety_level ∈ {read, plan, act}`; environment enforces.
    
- **Capability tokens**: `with:{caps:["move","grasp"]}` required for `act!`.
    
- **PII/Compliance**: `rule:HIPAA/GDPR` can be enforced by validator profiles.
    
- **Red teaming**: `judge{rule:abuse|privacy}` dry‑runs plan with adversarial prompts.
    

---

## 16. Linting & Style

- Prefer explicit `ag`, `obj`, `to`.
    
- Keep `conf`, `risk` where decisions or actions occur.
    
- Use named policies: `rule:safe`, `rule:orgPolicy123`.
    
- Provide `note` for human‑facing ops.
    

---

## 17. Worked Examples

**Inventory query**

```
see{ag:bot obj:fridge rule:inventory}? -> filter{obj:food rule:time<10m}
```

**Meal decision with tradeoff**

```
decide{ag:planner obj://ramen//bibimbap to:meal
       rule:{health:0.6,taste:0.4} why:hurry conf:0.72}! -> act{ag:chef}
```

**Robot cut with safety**

```
act{ag:arm1 obj:potato state:cut size:2cm
    with:{tool:knife} risk:{slip:0.1,burn:0.05}
    rule:guardOn when:{start:2025-10-25T09:00+09:00}}! -> check{rule:safe}
```

**Data pipeline**

```
fetch{src:"s3://bucket/x.csv"}?; filter{rule:age>=18}.; group{rule:by(country)}.; notify{to:"#ops" note:"refresh ok"}!
```

---

## 18. Standard Verb Signatures (excerpt)

- `see(Thing, Rule?) -> Thing|Measure, sidefx:read`
    
- `want(Goal) -> Plan, sidefx:none`
    
- `set(name, value) -> ok, sidefx:state`
    
- `decide(Options, Rule?, Why?, Risk?, Conf?) -> Choice, sidefx:none`
    
- `check(Thing|Rule) -> ok|fail(reason), sidefx:none`
    
- `learn(Data, Rule?) -> Model, sidefx:compute`
    
- `map(Input, Rule?) -> Output, sidefx:compute`
    
- `link(A,B, Rule?) -> Relation, sidefx:none`
    
- `judge(Thing, Rule) -> score in [0,1], sidefx:none`
    
- `act(Thing, Feat*, Risk?, Rule?) -> Outcome, sidefx:world`
    
- `recover(Target) -> Outcome, sidefx:world`
    
- `end(Plan|Proc) -> ok, sidefx:state`
    

---

## 19. Test Vectors (Parsing)

1. `see{obj:fridge rule:inventory}?` ✅
    
2. `decide{obj://a//b// rule:{x:0.7,y:0.3}}.` ✅
    
3. `act{ag:arm obj:potato size:2cm}!` ❌ `E013` (missing safety)
    
4. `act{ag:arm obj:potato size:2sm}!` ❌ `E005` (unit)
    

---

## 20. Versioning & Compatibility

- Header line (optional): `#! AILO 0.9 profile:strict` at file start
    
- Semver: breaking grammar → major; slot/verb additions → minor
    
- Profiles: `strict` (safety gates on), `lab` (looser), `sim` (no act!)
    

---

## 21. Minimal Parser/Emitter Notes

- Lexer is whitespace‑insensitive except inside strings.
    
- Keep comments to end‑of‑line with `#`.
    
- Preserve `id` when re‑emitting to maintain traceability.
    

---

## 22. Quick Cheat Sheet

```
VERB{ag:_, obj:_, to:_, state:_, why:_, rule:_, gain:_, risk:_, if:_, when:_, where:_, with:_, limit:_, cost:_, conf:_, src:_, ref:_, note:_} MOOD
```

- `?` ask, `.` tell, `!` do
    
- `//a//b//` choose, `->` expected, `~` approx
    
- Always add `rule` or `risk` before `!`
    

---

## 23. Appendix A: CJON Schema (JSON Schema draft‑07)

```json
{
  "$schema":"http://json-schema.org/draft-07/schema#",
  "title":"AILO Action",
  "type":"object",
  "required":["verb","slots"],
  "properties":{
    "verb":{"type":"string"},
    "mood":{"enum":["?","!","."]},
    "slots":{"type":"object"},
    "hint":{"type":"object"}
  },
  "additionalProperties":false
}
```

---

## 24. Appendix B: Example .ailo File

```
#! AILO 0.9 profile:strict
see{ag:bot obj:fridge rule:inventory}? # query stock
filter{obj:food rule:time<10m}. # keep quick items
decide{obj://ramen//bibimbap// to:meal rule:{health:0.6,taste:0.4} why:hurry conf:0.72}.
act{ag:chef obj:ramen state:boil time:7m with:{pot:"A1"} risk:{overcook:0.2} rule:safe}! -> notify{to:"#kitchen"}
```

---

## 25. End Edition Declaration (v0.9-E)

**Status:** Finalized implementation reference (operational)  
**Philosophy:** No roadmap. No placeholders. Only finalized behavior.  
**Scope:** Grammar · Transport · Validation · Security · Execution

- Conformant encoders/decoders MUST produce identical canonical bytes and hash.
    
- All SRM computations MUST be reproducible within ±0.001.
    

---

## 26. Unified Execution Stack

|Layer|Function|Implementation|
|---|---|---|
|**AILO**|Intent grammar (`Verb{Slot*}Mood`)|Reference parser (`scp-core`)|
|**SCP**|Serialization + compression|CJON/MessagePack canonical encoder|
|**Validation**|SRM · rule · risk checks|Adaptive SRM engine v2|
|**Security**|AES-256-GCM + ECDSA-P256 + Curve25519|Built-in crypto provider|
|**Trace**|Immutable ledger (hash-chain)|Local JSONL + Merkle anchor|
|**Runtime**|CLI + REST + gRPC|scp-runtime v0.9-E|

---

## 27. Deterministic Commit Rule (reinforced)

- Any `!` action MUST include **at least one** of `{rule, risk, conf}`; else `E013`.
    
- Canonical slot order MUST be preserved for hashing and CJON emission.
    
- Choice `//…//` MUST be resolved **before** commit.
    

**Example**

```ailo
act{ag:arm1 obj:apple state:slice size:1cm
    rule:safe risk:{cut:0.05} conf:0.96
    with:{tool:knife}}!
```

---

## 28. Canonical Packet (Lossless)

```json
{
  "version":"SCP 0.9-E",
  "sr":{
    "verb":"act","mood":"!",
    "slots":{
      "ag":"arm1","obj":"apple",
      "state":{"slice":true,"size":{"value":1,"unit":"cm"}},
      "rule":"safe","risk":{"cut":0.05},"conf":0.96,
      "with":{"tool":"knife"}
    }
  },
  "meta":{"ts":"2025-10-27T10:00:00Z","profile":"secure"},
  "hash":"sha3-256:b21f...",
  "sig":"ecdsa-p256:MEYCIQ..."
}
```

> Every conformant encoder must re-emit **identical JSON bytes and hash**.

---

## 29. Validation Rules (locked)

|Code|Meaning|Enforcement|
|---|---|---|
|**E002**|Unknown verb|reject|
|**E005**|Unit mismatch|reject|
|**E013**|Unsafe commit|reject|
|**E031**|SRM < 0.95|revalidate|
|**E045**|Signature mismatch|reject|
|**E048**|Schema fail|reject|

- SRM via cosine similarity; **drift guard** Δ≤0.1.
    

---

## 30. Security Stack (finalized)

```
Key exchange:  Curve25519 ECDH
Symmetric:     AES-256-GCM
Signature:     ECDSA-P256
Hash:          SHA-3-256
Key lifetime:  24 h or 1000 sessions
```

_All crypto operations are deterministic; any deviation invalidates the packet._

---

## 31. Execution Flow (real-time)

```
Input → Parse → Validate → Encrypt → Trace → Act → Log
```

**Sample runtime output**

```json
{
  "ok":true,
  "profile":"secure",
  "srm":0.976,
  "cr":4.6,
  "rt_ms":84,
  "trace_id":"trc-2025-10-27-A01",
  "hash":"sha3-256:b21f..."
}
```

---

## 32. Compliance Profiles (frozen)

|Profile|SRM ≥|Security|Trace|Mode|
|---|---|---|---|---|
|**strict**|0.95|AES-GCM|local|research|
|**secure**|0.98|AES-GCM + ECDSA|full|deploy|
|**sim**|n/a|none|mock|dry-run|

Profiles are **immutable** in v0.9-E.

---

## 33. Conformance Checklist

- ✅ Deterministic parser (same output hash on repeat)
    
- ✅ Validation passes all mandatory rules
    
- ✅ SRM reproducible within ±0.001
    
- ✅ AES-GCM + ECDSA verified
    
- ✅ Trace hash-chain intact
    
- ✅ p95 latency ≤ 120 ms
    
- ✅ Profiles `strict/secure` honored
    

---
