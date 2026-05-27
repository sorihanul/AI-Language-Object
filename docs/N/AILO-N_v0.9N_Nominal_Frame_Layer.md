# AILO-N v0.9N — Nominal Frame Layer

> **Purpose**
> A nominal frame layer for AILO v0.9E++. AILO-N defines object frames using noun-style identifiers and slot-based relations. It is designed to represent reusable targets, formal-structure views, and structured context packets for AILO intents.

---

## 0) License

MIT © 2026. Use/modify/distribute with attribution; no warranty.

---

## 1) System Overview

**AILO-N** is a nominal frame layer for AILO. It complements the existing AILO intent grammar without replacing it.

AILO v0.9E++ uses intent-centered verb forms:

```ailo
Verb { ag, obj, to, rule, risk, conf, with, when, id,
       nuance, tone, emotion, context,
       fidelity, style, memory, trace }
Mood
```

AILO-N adds noun-style object frames:

```ailo
Noun.Frame {
  slot:value,
  slot:[value1,value2],
  state:"candidate",
  conf:0.91
};
```

**Core ideas**: Nominal Frames · Slot-Determined Meaning · Formal Structure View · Target Reuse · Context Compression · Validation Compatibility

**Targets**: GPT / Gemini / Claude / Llama / SLMs, model-agnostic

**Design**: Additive layer. AILO-N does not change the existing `?`, `.`, `!` intent mood model. It introduces `;` as the noun-frame terminator.

---

## 2) AILO-N Grammar

### 2.1 Canonical Form

```ailo
Noun.Frame {
  id,
  label,
  alias,
  isa,
  kind,
  role,
  priority,
  subject,
  predicate,
  object,
  content,
  partOf,
  contains,
  dependsOn,
  requires,
  governedBy,
  governs,
  conflictsWith,
  supports,
  blocks,
  allows,
  routesTo,
  overrides,
  consumes,
  produces,
  transforms,
  enables,
  prevents,
  provides,
  validates,
  stores,
  retrieves,
  useFor,
  must,
  cannot,
  should,
  scope,
  risk,
  rule,
  topo,
  validWhen,
  invalidWhen,
  source,
  evidence,
  note,
  state,
  conf,
  assertedBy,
  assertionBasis,
  reviewedAt,
  createdAt,
  updatedAt,
  version,
  memory,
  trace,
  context,
  nuance,
  tone,
  emotion,
  style,
  fidelity
};
```

The canonical form is the common slot surface. Domain-specific packs may add profile-bound extension slots such as `domain`, `range`, `inverse`, `transitive`, `topic`, `author`, or `goal` only when a slot contract defines how they should be read and validated.

### 2.2 Terminators

| Terminator | Layer           | Meaning          |
| ---------- | --------------- | ---------------- |
| `?`        | AILO-V          | query            |
| `.`        | AILO-V / report | assert or report |
| `!`        | AILO-V          | execute          |
| `;`        | AILO-N          | close noun frame |

Example:

```ailo
Engine.Builder{
  isa:Engine,
  dependsOn:[Module.Core],
  governedBy:[Policy.Primary],
  produces:[Artifact.EngineCard],
  state:"candidate",
  conf:0.91
};

verify{
  obj:Engine.Builder,
  rule:{check:"structure_consistency"},
  trace:{level:"full"}
}!
```

---

## 3) Design Principles

### 3.1 Slot-Determined Meaning

In AILO-N, the frame name is a reference handle. The slots determine the operational meaning of the frame.

```ailo
Claim.SampleSignal{
  isa:Claim,
  subject:Dataset.SampleMarket,
  predicate:"sample_signal",
  evidence:[Source.ExchangeData],
  state:"candidate",
  conf:0.62
};
```

In this example, `Claim.SampleSignal` is the frame handle. The meaning is determined by `isa`, `subject`, `predicate`, `evidence`, `state`, and `conf`.

### 3.2 Read-on-Arrival Structure

AILO-N uses explicit words rather than opaque symbols. The format is intended to be readable by AI systems without prior training on a separate symbolic codebook.

Recommended:

```ailo
Engine.Builder{
  isa:Engine,
  dependsOn:[Module.Core],
  governedBy:[Policy.Primary]
};
```

Not recommended:

```ailo
□EF ⊃ IC ⚑ NK;
```

### 3.3 Additive Layer

AILO-N does not replace AILO verbs. It provides reusable targets for AILO verbs.

```ailo
Document.ReportA{
  isa:Document,
  topic:[Concept.Structure, Concept.AI],
  state:"observed"
};

summarize{
  obj:Document.ReportA,
  rule:{focus:[Concept.Structure, Concept.AI]}
}!
```

`topic` is a profile-bound extension slot. See `14.2 extension.slots.ailon`.

---

## 4) Core Slots

### 4.1 Identity Slots

| Slot    | Meaning              |
| ------- | -------------------- |
| `id`    | stable identifier    |
| `label` | human-readable label |
| `alias` | alternate names      |
| `isa`   | type or class        |
| `kind`  | subtype or kind      |
| `role`  | functional role      |

Example:

```ailo
System.AILO{
  id:"System.AILO",
  label:"AILO",
  alias:["AILO Runtime","AILO Control Language"],
  isa:System,
  role:"intent_centric_control_language",
  state:"candidate"
};
```

### 4.2 Claim and Content Slots

| Slot        | Meaning                            |
| ----------- | ---------------------------------- |
| `subject`   | claim or relation subject          |
| `predicate` | claim or relation predicate        |
| `object`    | claim or relation object           |
| `content`   | textual content or claim body      |
| `note`      | annotation or short explanation    |

Example:

```ailo
Claim.SampleSignal{
  isa:Claim,
  subject:Dataset.SampleMarket,
  predicate:"sample_signal",
  object:Flow.CapitalOutflow,
  content:"A sample signal indicates a possible capital outflow.",
  note:"Use as a test claim, not as a real market fact.",
  state:"candidate"
};
```

### 4.3 Relation Slots

| Slot            | Meaning                            |
| --------------- | ---------------------------------- |
| `partOf`        | belongs to a larger structure      |
| `contains`      | includes components                |
| `dependsOn`     | requires another frame to function |
| `requires`      | requires a condition or resource   |
| `governedBy`    | is controlled by a policy          |
| `governs`       | controls another frame             |
| `conflictsWith` | conflicts with another frame       |
| `supports`      | supports another frame             |
| `blocks`        | blocks another frame or action     |
| `allows`        | allows another frame or action     |
| `routesTo`      | routes to another frame            |
| `overrides`     | overrides another frame or rule    |

Example:

```ailo
Policy.Safety{
  isa:Policy,
  governs:[Engine.Builder, Engine.Analyzer],
  blocks:[Action.UnsafeDisclosure, Action.UnsafeExecution],
  overrides:[Policy.LocalPreference],
  state:"candidate",
  conf:0.96
};
```

### 4.4 Capability and Flow Slots

| Slot         | Meaning                           |
| ------------ | --------------------------------- |
| `consumes`   | accepted inputs                   |
| `produces`   | produced outputs                  |
| `transforms` | input-output conversion           |
| `enables`    | capabilities enabled by the frame |
| `prevents`   | conditions prevented by the frame |
| `provides`   | provided capability or interface  |
| `validates`  | validation targets or metrics     |
| `stores`     | stored objects                    |
| `retrieves`  | retrievable objects               |
| `useFor`     | recommended tasks or use cases    |

Example:

```ailo
Engine.Translator{
  isa:Engine,
  consumes:[Text.Source],
  produces:[Text.Translated],
  validates:[Metric.SRM, Metric.AffSRM, Metric.FID],
  state:"candidate"
};
```

### 4.5 Constraint Slots

| Slot          | Meaning               |
| ------------- | --------------------- |
| `must`        | required condition    |
| `cannot`      | forbidden condition   |
| `should`      | recommended condition |
| `scope`       | scope of validity     |
| `risk`        | risk profile          |
| `rule`        | associated rule       |
| `priority`    | priority level or ordering hint |
| `topo`        | optional relation-topology hint |
| `validWhen`   | validity condition    |
| `invalidWhen` | invalidity condition  |

Example:

```ailo
Memory.LongTerm{
  isa:ContextLayer,
  must:[Consent.Required, Relevance.High],
  cannot:[Store.SensitivePersonalData],
  scope:"cross_session_context",
  risk:"privacy_sensitive",
  state:"candidate"
};
```

### 4.6 Evidence and State Slots

| Slot        | Meaning                     |
| ----------- | --------------------------- |
| `state`     | frame status                |
| `conf`      | confidence hint, 0.0 to 1.0 |
| `source`    | source reference            |
| `evidence`  | supporting evidence         |
| `note`      | annotation or review note   |
| `version`   | version label               |
| `trace`     | trace setting               |
| `memory`    | memory hint                 |
| `createdAt` | creation timestamp          |
| `updatedAt` | update timestamp            |

Example:

```ailo
Claim.AILO_N_ContextUse{
  isa:Claim,
  content:"AILO-N represents selected formal-structure views as noun-slot frames for AILO intents.",
  evidence:[Source.DesignNote],
  state:"candidate",
  conf:0.74
};
```

---

## 5) Frame States

AILO-N uses explicit frame states.

| State        | Meaning                             |
| ------------ | ----------------------------------- |
| `observed`   | extracted or observed from input    |
| `candidate`  | proposed but not verified           |
| `asserted`   | accepted for current system context |
| `inferred`   | derived by a rule or graph process  |
| `deprecated` | retained but no longer recommended  |
| `rejected`   | failed validation                   |

### 5.1 Assertion Basis

`state:"asserted"` should not mean "the model feels confident." It means the frame has been accepted for the current system context through a visible basis.

Recommended assertion fields:

| Slot             | Meaning                                  |
| ---------------- | ---------------------------------------- |
| `assertedBy`     | agent, tool, reviewer, or process        |
| `assertionBasis` | validation rule, evidence, or review     |
| `reviewedAt`     | review timestamp or version marker       |

Example:

```ailo
Claim.SampleSignal{
  isa:Claim,
  subject:Dataset.SampleMarket,
  predicate:"sample_signal",
  object:Flow.CapitalOutflow,
  state:"candidate",
  conf:0.58
};
```

After validation:

```ailo
Claim.SampleSignal{
  isa:Claim,
  subject:Dataset.SampleMarket,
  predicate:"sample_signal",
  object:Flow.CapitalOutflow,
  evidence:[Source.ExchangeData],
  state:"asserted",
  assertedBy:Validator.SourceCheck,
  assertionBasis:["evidence_required","source_match"],
  reviewedAt:"2026-05-26",
  conf:0.88
};
```

---

## 6) Formal Structure Mapping

AILO-N can represent selected formal structure elements as frames. It does not replace the external formal source.

| Formal Element      | AILO-N Representation                         |
| ------------------- | --------------------------------------------- |
| Class               | value of `isa`                                |
| Individual          | `Noun.Frame`                                  |
| Object Property     | relation slot                                 |
| Data Property       | value slot                                    |
| Axiom               | `rule` or validator rule                      |
| Constraint          | `must`, `cannot`, `validWhen`, validator rule |
| Annotation          | `label`, `alias`, `source`, `note`            |
| Inferred Fact       | `state:"inferred"`                            |
| Extracted Candidate | `state:"candidate"`                           |
| Accepted Fact       | `state:"asserted"`                            |

Formal-structure statement:

```text
BuilderModule type Engine
BuilderModule dependsOn CoreModule
BuilderModule governedBy PrimaryPolicy
```

AILO-N representation:

```ailo
Engine.Builder{
  isa:Engine,
  dependsOn:[Module.Core],
  governedBy:[Policy.Primary],
  state:"asserted",
  source:["formal_source:system_core"],
  assertedBy:Validator.StructureCheck,
  assertionBasis:["formal_source_match","relation_slots_bound"],
  reviewedAt:"2026-05-26"
};
```

---

## 7) Relation Contracts

Relation slots may be described as frames.

```ailo
Slot.dependsOn{
  isa:RelationSlot,
  domain:[Engine, Module, Task],
  range:[Engine, Module, Resource],
  inverse:"requiredBy",
  transitive:false,
  state:"candidate"
};
```

```ailo
Slot.governedBy{
  isa:RelationSlot,
  domain:[Engine, Module, ContextLayer, Task],
  range:[Policy],
  inverse:"governs",
  priority:"safety_relevant",
  state:"candidate"
};
```

Recommended relation contract set:

| Slot            | Inverse         |
| --------------- | --------------- |
| `contains`      | `partOf`        |
| `partOf`        | `contains`      |
| `dependsOn`     | `requiredBy`    |
| `requires`      | `requiredFor`   |
| `governedBy`    | `governs`       |
| `governs`       | `governedBy`    |
| `blocks`        | `blockedBy`     |
| `allows`        | `allowedBy`     |
| `produces`      | `producedBy`    |
| `consumes`      | `consumedBy`    |
| `conflictsWith` | `conflictsWith` |
| `supports`      | `supportedBy`   |

---

## 8) Runtime Integration

AILO-N adds a frame registration step to the existing runtime.

Existing runtime pattern:

```text
Parse → Plan → Execute → Validate → Trace → Persist
```

AILO-N integrated runtime pattern:

```text
Parse → Register Frames → Plan → Execute → Validate → Trace → Persist
```

### 8.1 Parser Types

```ts
export type AiloMood = "?" | "." | "!" | ";";

export type NounFrame = {
  kind: "noun_frame";
  name: string;
  slots: Record<string, any>;
  mood: ";";
};

export type VerbIntent = {
  kind: "verb_intent";
  verb: string;
  slots: Record<string, any>;
  mood: "?" | "." | "!";
};
```

### 8.2 Frame Registry

```ts
export type FrameRegistry = {
  frames: Record<string, NounFrame>;
  aliases: Record<string, string>;
  stateIndex: Record<string, string[]>;
  typeIndex: Record<string, string[]>;
};
```

### 8.3 Planner Behavior

```text
If an intent references a registered frame:
  attach selected frame slots as structured context.

If an intent requests specific slots:
  attach only the requested slots.

If frame.state == "candidate":
  require verification before fact-level use.

If frame.state == "asserted":
  allow as current structured context unless validation fails.
```

---

## 9) Validation Layer

AILO-N frames are validated before promotion or persistent use.

### 9.1 Validation Codes

| Code | Meaning                                 | Action                    |
| ---- | --------------------------------------- | ------------------------- |
| N001 | missing `isa`                           | warn or reject by profile |
| N002 | undefined target                        | reject                    |
| N003 | slot type mismatch                      | reject                    |
| N004 | relation domain mismatch                | reject                    |
| N005 | relation range mismatch                 | reject                    |
| N006 | naming mismatch                         | warn                      |
| N007 | asserted without source or assertion basis | warn or reject by profile |
| N008 | candidate used as fact                  | revalidate                |
| N009 | execution instruction inside noun frame | reject                    |
| N010 | invalid state transition                | reject                    |
| N011 | formal source conflict                  | reject                    |
| N012 | unknown unbound slot                    | warn or ignore            |

### 9.2 Example: Missing `isa`

```ailo
Engine.Builder{
  dependsOn:[Module.Core]
};
```

Validation result:

```text
N001 missing_isa
```

### 9.3 Example: Naming Mismatch

```ailo
Engine.Builder{
  isa:Policy,
  governs:[Engine.Analyzer]
};
```

Validation result:

```text
N006 naming_mismatch
```

### 9.4 Example: Execution Inside Frame

```ailo
Engine.Builder{
  isa:Engine,
  verify:true
};
```

Validation result:

```text
N009 execution_instruction_inside_noun_frame
```

Corrected form:

```ailo
Engine.Builder{
  isa:Engine
};

verify{obj:Engine.Builder}!
```

---

## 10) State Transition Rules

Recommended transitions:

```text
observed   → candidate
candidate  → asserted, only with source/evidence and assertion basis
candidate  → rejected
inferred   → asserted, only with verification basis
asserted   → deprecated
deprecated → asserted, if source and review are provided
rejected   → asserted, only with explicit override evidence
```

Validation example:

```ailo
verify{
  obj:Claim.SampleSignal,
  rule:{
    check:[
      "subject_type_valid",
      "predicate_allowed",
      "evidence_required",
      "no_conflict_with_formal_source"
    ]
  },
  trace:{level:"full"}
}!
```

Promotion example:

```ailo
promote{
  obj:Claim.SampleSignal,
  to:"asserted",
  with:[Source.ExchangeData],
  rule:{basis:["evidence_required","source_match"]},
  ag:Validator.SourceCheck,
  risk:"low"
}!
```

---

## 11) Memory and Trace

AILO-N frames may use existing AILO memory and trace slots.

```ailo
Project.AILO_N{
  isa:Project,
  goal:"Nominal Frame Layer for AILO",
  memory:{long:true, reflect:false},
  trace:{level:"full"},
  state:"candidate",
  conf:0.93
};
```

Recommended memory behavior:

```text
short   = current task or session context
long    = stable project knowledge
reflect = design review, failure modes, improvement notes
```

Recommended trace behavior:

```text
record frame creation
record source references
record validation results
record verb intents that used the frame
record state transitions
```

---

## 12) Context Packet Generation

AILO-N can produce compact context packets for AILO-V intents.

Frame:

```ailo
Policy.Primary{
  isa:Policy,
  governs:[Engine.Builder],
  blocks:[Action.UnsafeDisclosure, Action.UnsafeExecution],
  priority:"global",
  state:"asserted",
  source:[Source.PolicyNote],
  assertedBy:Validator.PolicyCheck,
  assertionBasis:["source_visible","blocks_declared"],
  reviewedAt:"2026-05-26",
  conf:0.96
};
```

Compression intent:

```ailo
compress{
  obj:Policy.Primary,
  rule:{preserve:[isa, governs, blocks, priority, state, conf], budget:"500tokens"},
  to:"llm_context_packet"
}!
```

Possible packet:

```text
Policy.Primary is a Policy.
It governs Engine.Builder.
It blocks UnsafeDisclosure and UnsafeExecution.
Its priority is global.
State: asserted.
Confidence: 0.96.
```

---

## 13) Recommended Frame Types

Initial recommended frame types:

```text
System
Module
Engine
Policy
ContextLayer
Task
Input
Output
Artifact
Claim
Source
Rule
Metric
Context
Project
Book
Person
Concept
Document
TextSegment
Action
Capability
FrameSystem
Report
Validator
```

Meta/profile-bound types such as `RelationSlot`, `ExtensionSlot`, `MappingRule`, `Organization`, `Dataset`, `Flow`, `Consent`, `Relevance`, and `Store` may be declared by slot contracts or domain profiles before persistent validation.

Example:

```ailo
Module.ContextLayer{
  isa:Module,
  role:"stateful_memory_layer",
  dependsOn:[Policy.Primary],
  provides:[Capability.ContextContinuity],
  state:"candidate",
  conf:0.94
};
```

Example:

```ailo
Book.SampleWork{
  isa:Book,
  author:Person.SampleAuthor,
  topic:[Concept.FastMode, Concept.SlowMode, Concept.JudgmentBias],
  useFor:[Task.CriticalReview, Task.ReadingGuide],
  state:"candidate"
};
```

---

## 14) Knowledge Pack Shape

Suggested file tree:

```text
/ailo
  ├─ runtime/
  ├─ adapters/
  ├─ knowledge/
  ├─ knowledge-n/
  │   ├─ noun.frames.ailon
  │   ├─ slot.contracts.ailon
  │   ├─ formal.mapping.ailon
  │   ├─ frame.validation.rules.json
  │   ├─ state.transition.rules.json
  │   └─ examples/
  ├─ cli/
  ├─ api/
  └─ examples/
```

### 14.1 `slot.contracts.ailon`

```ailo
Slot.dependsOn{
  isa:RelationSlot,
  domain:[Engine, Module, Task],
  range:[Engine, Module, Resource],
  inverse:"requiredBy",
  state:"candidate"
};

Slot.governedBy{
  isa:RelationSlot,
  domain:[Engine, Module, ContextLayer, Task],
  range:[Policy],
  inverse:"governs",
  state:"candidate"
};
```

### 14.2 `extension.slots.ailon`

Profile-bound extension slots must be declared before persistent use. They are allowed when a profile needs them, but they are not part of the common canonical surface.

```ailo
Slot.topic{
  isa:ExtensionSlot,
  domain:[Document, Book, Project, Context],
  range:[Concept, TextSegment],
  useFor:[Task.RouteSelection, Task.ContextCompression],
  state:"candidate"
};

Slot.author{
  isa:ExtensionSlot,
  domain:[Book, Document, TextSegment],
  range:[Person, Organization],
  useFor:[Task.SourceAttribution],
  state:"candidate"
};

Slot.goal{
  isa:ExtensionSlot,
  domain:[Project, Task, FrameSystem],
  range:[TextSegment, Concept],
  useFor:[Task.ScopeLock, Task.Validation],
  state:"candidate"
};
```

### 14.3 `formal.mapping.ailon`

```ailo
Mapping.ClassToIsa{
  isa:MappingRule,
  from:"formal_source:Class",
  to:"AILO-N:isa",
  state:"candidate"
};

Mapping.PropertyToSlot{
  isa:MappingRule,
  from:"formal_source:ObjectProperty",
  to:"AILO-N:relation_slot",
  state:"candidate"
};
```

---

## 15) Quick Recipes

### 15.1 Register a Reusable Target

```ailo
Document.ReportA{
  isa:Document,
  topic:[Concept.Structure, Concept.AI],
  state:"observed",
  source:[Source.UploadedFile]
};
```

`topic` is a profile-bound extension slot. See `14.2 extension.slots.ailon`.

### 15.2 Verify a Candidate Claim

```ailo
Claim.NewRelation{
  isa:Claim,
  subject:Engine.Builder,
  predicate:"dependsOn",
  object:Module.Helper,
  evidence:[Source.DesignNote],
  state:"candidate",
  conf:0.71
};

verify{
  obj:Claim.NewRelation,
  rule:{check:["subject_type_valid","predicate_allowed","evidence_required"]},
  to:"promotion_verdict"
}!
```

### 15.3 Compress for LLM Context

```ailo
compress{
  obj:[Engine.Builder, Policy.Primary],
  rule:{preserve:[isa, dependsOn, governedBy, blocks, priority, state, conf], budget:"900tokens"},
  to:"llm_context_packet"
}!
```

---

## 16) Operational Guidance

Use AILO-N when:

* a target appears repeatedly across intents
* selected formal structure context must be passed to an AI model
* relation direction must be preserved
* state, source, and confidence need to remain visible
* a candidate structure must be verified before assertion
* context size needs to be controlled

Avoid AILO-N when:

* the request is single-use and simple
* no reusable target is needed
* a frame would only duplicate unstructured notes
* validation rules are not available for persistent use
* execution intent is being placed inside a noun frame

---

## 17) Minimal Working Example

```ailo
Engine.Builder{
  isa:Engine,
  role:"engine_builder",
  dependsOn:[Module.Core],
  governedBy:[Policy.Primary],
  produces:[Artifact.EngineCard],
  state:"asserted",
  source:[Source.DesignNote],
  assertedBy:Validator.StructureCheck,
  assertionBasis:["required_slots_present","policy_bound"],
  reviewedAt:"2026-05-26",
  conf:0.91
};

Policy.Primary{
  isa:Policy,
  governs:[Engine.Builder],
  blocks:[Action.UnsafeDisclosure, Action.UnsafeExecution],
  priority:"global",
  state:"asserted",
  source:[Source.PolicyNote],
  assertedBy:Validator.PolicyCheck,
  assertionBasis:["source_visible","blocks_declared"],
  reviewedAt:"2026-05-26",
  conf:0.96
};

verify{
  obj:Engine.Builder,
  rule:{check:[isa, dependsOn, governedBy, produces]},
  to:"verdict"
}!

compress{
  obj:[Engine.Builder, Policy.Primary],
  rule:{preserve:[isa, dependsOn, governedBy, blocks, priority, state, conf], budget:"900tokens"},
  to:"llm_context_packet"
}!
```

---

## 18) Fixture Set

These fixtures are small examples for checking whether AILO-N remains a target-frame layer instead of becoming an execution prompt.

### 18.1 Verification Frame

```ailo
Validator.EvidenceCheck{
  isa:FrameSystem,
  role:"evidence_first_verification",
  consumes:[Artifact.Target, Rule.AcceptanceCriteria],
  produces:[Report.Validation],
  governedBy:[Policy.EvidenceRequired],
  state:"candidate",
  source:[Source.DesignNote],
  conf:0.72
};

verify{
  obj:Validator.EvidenceCheck,
  rule:{check:[isa, role, consumes, produces, governedBy, source]},
  to:"frame_verdict"
}!
```

### 18.2 Reusable Note Frame

```ailo
Document.ReusableNote{
  isa:Document,
  kind:"reusable_note",
  content:"A reusable rule should keep source, state, and confidence visible.",
  useFor:[Task.ContextRecall, Task.RouteSelection],
  source:[Source.SessionSummary],
  state:"candidate",
  conf:0.66
};

promote{
  obj:Document.ReusableNote,
  to:"asserted",
  with:[Source.SessionSummary],
  rule:{basis:["reuse_value","source_visible"]},
  ag:Validator.ValidationGate
}!
```

### 18.3 Frame Builder Example

```ailo
Frame.Builder{
  isa:FrameSystem,
  role:"purpose_bounded_frame_design",
  consumes:[Input.UserGoal, Source.LocalAssets],
  produces:[Artifact.FrameSystemBlueprint, Artifact.BootSurface],
  prevents:[Action.OverBroadBuild, Action.UnverifiedPromotion],
  state:"candidate",
  conf:0.7
};

compress{
  obj:Frame.Builder,
  rule:{preserve:[isa, role, consumes, produces, prevents, state, conf], budget:"600tokens"},
  to:"llm_context_packet"
}!
```

---

## 19) FAQ

**Q:** Does AILO-N replace AILO verbs?
**A:** No. AILO-N defines noun frames. AILO verbs continue to perform query, report, and execution intents.

**Q:** Does AILO-N replace external formal sources?
**A:** No. AILO-N can represent selected formal-structure views as readable object frames, but the source remains external.

**Q:** Does the frame name determine meaning?
**A:** No. The frame name is a handle. Meaning is determined by slots.

**Q:** Can unknown slots be used?
**A:** Yes, but unknown slots should be ignored, warned, or bound by a slot contract depending on the validation profile.

**Q:** Can candidate frames be used as facts?
**A:** Not without verification. Candidate frames require validation before fact-level use.

---

## 20) Changelog

### v0.9N

* Added noun-frame syntax with `;` terminator
* Added slot-determined meaning principle
* Added formal-structure-to-frame mapping rules
* Added frame state model
* Added relation contract frames
* Added runtime frame registration step
* Added noun-frame validation codes
* Added context packet generation workflow

---

## 21) Summary

AILO-N is a noun-slot frame layer for AILO.

A noun frame provides a stable handle.
Slots determine meaning.
State indicates status.
Confidence provides a confidence hint.
Source and evidence provide grounding.
AILO verbs use noun frames as structured targets.

**AILO-N turns selected formal structure context into readable, reusable, and validated object frames for AILO intents.**

