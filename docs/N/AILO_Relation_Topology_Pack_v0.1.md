# AILO Relation Topology Pack v0.1

## Thin Relation-Topology Hint Pack for AILO-N

MIT © 2026. Use, modify, and distribute with attribution. No warranty.

---

## 0) Purpose

**AILO Relation Topology Pack** is a thin optional extension pack for AILO-N.

It does not create a new AILO layer.
It does not replace AILO-N relation slots.
It does not add execution behavior.

It adds one optional hint slot:

```ailo
topo:{...}
```

The purpose of `topo` is to mark the structural function of a frame inside a surrounding relation network.

AILO-N defines reusable target frames.
AILO-V performs actions on those frames.
The topology hint helps an AI system understand how frames are positioned through relationships such as center, bridge, gate, cut, loop, anchor, and sink.

---

## 1) Core Definition

```text
AILO Relation Topology =
A light relation-structure hint inside AILO-N that describes how a frame functions within a network of other frames.
```

A topology hint answers this question:

```text
What structural function does this frame perform in the surrounding relation network?
```

It does not answer:

```text
What is this frame?
What is the exact relation slot?
What action should be executed?
```

Those remain handled by AILO-N frame slots and AILO-V verbs.

---

## 2) Design Rule

### 2.1 Thin Absorption Rule

AILO relation topology must be absorbed into AILO-N as a thin optional slot.

Recommended:

```ailo
Frame.Name{
  isa:Type,
  state:"candidate",
  topo:{rel:"bridge"}
};
```

Not recommended:

```text
Create a separate mandatory AILO-Topo grammar layer.
```

### 2.2 Non-Replacement Rule

`topo` does not replace relation slots.

Relation slots define actual relations:

```ailo
supports:[Claim.Core]
blocks:[Action.UnverifiedAssertion]
dependsOn:[Module.Core]
governedBy:[Policy.Primary]
```

`topo` describes the structural function of those relations:

```ailo
topo:{rel:"anchor"}
topo:{rel:"gate"}
topo:{rel:"chain"}
topo:{rel:"cut"}
```

### 2.3 Optionality Rule

`topo` is optional.

Use it only when relation structure improves routing, compression, validation, memory continuity, project mapping, or creative continuity.

Avoid it when the frame is simple, temporary, or single-use.

### 2.4 Domain Profile Declaration Rule

Domain-specific frame types and slots used in examples must be declared by a domain profile before strict validation.

Examples include:

```text
types:
Theory
Pattern
Conflict
Character
Motif
Theme
Draft
Review
Revision
Verdict
Evidence
Criticism
State

slots:
title
from
conflict
```

These examples are allowed as profile-bound material. They are not added to the common AILO-N canonical surface by this pack.

---

## 3) Minimal Syntax

### 3.1 Minimal Form

```ailo
topo:{rel:"hub"}
```

### 3.2 Recommended Form

```ailo
topo:{
  rel:"hub|chain|bridge|gate|loop|cut|anchor|sink",
  to:[FrameRef],
  strength:"weak|medium|strong|hard"
}
```

### 3.3 Field Meaning

| Field | Meaning |
|---|---|
| `rel` | relation-topology function of the frame |
| `to` | target frames affected or connected by this topology hint |
| `strength` | structural strength of the topology function |

Only `rel` is required when `topo` is used.

---

## 4) Relation Topology Types

### 4.1 `hub`

A frame that gathers or organizes multiple related frames.

Use when the frame functions as a relation center.

```ailo
Concept.DualProcess{
  isa:Concept,
  supports:[Claim.System1Fast, Claim.System2Deliberate],
  state:"candidate",
  topo:{
    rel:"hub",
    to:[Claim.System1Fast, Claim.System2Deliberate],
    strength:"strong"
  }
};
```

### 4.2 `chain`

A frame that belongs to a sequential relation path.

Use when order, dependency, or procedural flow matters.

```ailo
Task.BookResearch{
  isa:Task,
  requires:[Book.Target, Source.Primary],
  produces:[Report.BookResearch],
  state:"candidate",
  topo:{
    rel:"chain",
    to:[Book.Target, Source.Primary, Claim.Extracted, Report.BookResearch],
    strength:"strong"
  }
};
```

### 4.3 `bridge`

A frame that connects two frames, domains, stages, or representation layers.

Use when a frame transfers structure between areas.

```ailo
Mapping.BookToReport{
  isa:MappingRule,
  from:Book.Target,
  to:Report.BookResearch,
  state:"candidate",
  topo:{
    rel:"bridge",
    to:[Book.Target, Report.BookResearch],
    strength:"medium"
  }
};
```

### 4.4 `gate`

A frame that controls whether a transition or relation can proceed.

Use for validation, promotion, permission, and policy-controlled passage.

```ailo
Policy.EvidenceRequired{
  isa:Policy,
  blocks:[Action.AssertWithoutEvidence],
  allows:[Action.PromoteWithEvidence],
  state:"asserted",
  source:[Source.PolicyNote],
  evidence:[Rule.EvidenceRequired],
  assertedBy:Validator.PolicyCheck,
  assertionBasis:["source_visible","promotion_gate_defined"],
  reviewedAt:"2026-05-27",
  topo:{
    rel:"gate",
    to:[State.Candidate, State.Asserted],
    strength:"hard"
  }
};
```

### 4.5 `loop`

A frame that represents a repeating or cyclic relation structure.

Use for revision cycles, review loops, recurring patterns, or repeated behavior.

```ailo
Pattern.RevisionLoop{
  isa:Pattern,
  contains:[Draft.A, Review.A, Revision.A],
  state:"observed",
  topo:{
    rel:"loop",
    to:[Draft.A, Review.A, Revision.A],
    strength:"medium"
  }
};
```

### 4.6 `cut`

A frame that blocks, breaks, excludes, or invalidates a relation path.

Use for conflicts, contradictions, policy blocks, or invalid transitions.

```ailo
Conflict.SourceMismatch{
  isa:Conflict,
  conflictsWith:[Claim.AuthorThesis],
  state:"candidate",
  topo:{
    rel:"cut",
    to:[Claim.AuthorThesis],
    strength:"hard"
  }
};
```

### 4.7 `anchor`

A frame that grounds relation interpretation.

Use for sources, evidence, stable decisions, verified references, or canonical definitions.

```ailo
Source.PrimaryText{
  isa:Source,
  supports:[Claim.Core],
  state:"asserted",
  source:[Source.PrimaryText],
  evidence:[Evidence.DirectReference],
  assertedBy:Validator.SourceCheck,
  assertionBasis:["primary_source_visible","supports_target_claim"],
  reviewedAt:"2026-05-27",
  topo:{
    rel:"anchor",
    to:[Claim.Core],
    strength:"strong"
  }
};
```

### 4.8 `sink`

A frame where outputs, claims, sources, decisions, or results accumulate.

Use for reports, artifacts, memory records, summaries, or final output targets.

```ailo
Report.BookResearch{
  isa:Report,
  contains:[Claim.Core, Source.Primary, Criticism.Academic],
  state:"candidate",
  topo:{
    rel:"sink",
    to:[Claim.Core, Source.Primary, Criticism.Academic],
    strength:"strong"
  }
};
```

---

## 5) Recommended `strength` Values

| Value | Meaning |
|---|---|
| `weak` | light or optional structural hint |
| `medium` | useful structural hint for routing or compression |
| `strong` | important structural relation for task continuity |
| `hard` | blocking, controlling, or required structural function |

Examples:

```ailo
topo:{rel:"anchor", strength:"weak"}
topo:{rel:"bridge", strength:"medium"}
topo:{rel:"hub", strength:"strong"}
topo:{rel:"gate", strength:"hard"}
```

Note: `support` is not part of the core `rel` set. Use `rel:"anchor"`, `rel:"bridge"`, or ordinary `supports:[...]` instead.

---

## 6) Compression Use

AILO relation topology can guide context compression.

Recommended preservation priority:

```text
1. anchor
2. gate
3. cut
4. hub
5. sink
6. bridge
7. chain
8. loop
```

Example:

```ailo
compress{
  obj:Project.AILO_N,
  rule:{
    preserve_topo:["anchor","gate","cut","hub","sink"],
    budget:"1200tokens"
  },
  to:Context.ProjectPacket
}!
```

Interpretation:

```text
Keep the frames that ground, control, block, organize, or collect the task structure.
Compress or omit lower-priority support frames when the budget is limited.
```

---

## 7) Validation Use

Topology hints can support validation planning.

Validation should check:

```text
anchor exists
anchor supports target claim
gate conditions are satisfied
cut conflicts are absent or resolved
sink output does not include unverified candidate claims as facts
```

Example validation intent:

```ailo
verify{
  obj:Claim.Core,
  rule:{
    check:[
      "anchor_exists",
      "gate_passed",
      "no_hard_cut",
      "state_transition_valid"
    ]
  },
  to:Verdict.ClaimCore
}!
```

Topology hints do not prove validity by themselves.
They help select which structural checks should be performed.

---

## 8) Engine Routing Use

Relation topology can help select a suitable engine or action pattern.

| `topo.rel` | Suggested processing style |
|---|---|
| `hub` | structural synthesis, concept mapping, summary assembly |
| `chain` | stepwise analysis, workflow execution, procedural reasoning |
| `bridge` | comparison, translation, mapping, cross-domain synthesis |
| `gate` | validation, policy check, state transition review |
| `loop` | iterative refinement, revision, feedback cycle handling |
| `cut` | critique, contradiction check, risk analysis |
| `anchor` | evidence review, source grounding, canonical reference check |
| `sink` | final report assembly, memory storage, artifact generation |

Example:

```ailo
route{
  obj:Task.BookResearch,
  rule:{use_topo:true},
  to:Engine.Selected
}!
```

---

## 9) Memory Use

Topology hints can guide what should be preserved in long-term project memory.

Recommended memory priority:

```text
Store anchors.
Store gates.
Store cuts.
Store hubs.
Store final sinks.
Compress chains.
Summarize loops as patterns.
Keep bridges when they connect major modules or domains.
```

Example:

```ailo
store{
  obj:Project.AILO_N,
  rule:{
    memory:"long",
    preserve_topo:["hub","anchor","gate","cut","sink"],
    compress_chain:true,
    summarize_loop:true
  },
  to:Memory.ProjectRegistry
}!
```

---

## 10) Creative Use

In creative work, topology hints can preserve relation continuity across characters, scenes, motifs, themes, and artifacts.

Example:

```ailo
Character.MainArtist{
  isa:Character,
  role:"main_artist",
  conflict:[Conflict.SelfExpression],
  state:"candidate",
  topo:{
    rel:"hub",
    to:[Song.BlueNote, Scene.EmptyStation, Motif.UnsentLetter],
    strength:"strong"
  }
};

Motif.UnsentLetter{
  isa:Motif,
  supports:[Theme.UnspokenEmotion],
  state:"observed",
  topo:{
    rel:"anchor",
    to:[Theme.UnspokenEmotion],
    strength:"medium"
  }
};

Conflict.SelfExpression{
  isa:Conflict,
  blocks:[Action.Confession],
  state:"candidate",
  topo:{
    rel:"cut",
    to:[Character.MainArtist, Action.Confession],
    strength:"strong"
  }
};
```

This allows a creative system to preserve relation structure across lyrics, album covers, character sheets, stories, and visual prompts.

---

## 11) Research and Book Analysis Use

In research and book analysis, topology hints can identify central concepts, grounding sources, conflicting claims, and report assembly points.

Example:

```ailo
Theory.DualProcess{
  isa:Theory,
  contains:[Concept.System1, Concept.System2],
  state:"candidate",
  topo:{
    rel:"hub",
    to:[Claim.System1Fast, Claim.System2Deliberate, Criticism.DualProcessLimit],
    strength:"strong"
  }
};

Source.OriginalBook{
  isa:Source,
  supports:[Claim.System1Fast],
  state:"asserted",
  source:[Source.BibliographicRecord],
  evidence:[Evidence.DirectTextReference],
  assertedBy:Validator.SourceCheck,
  assertionBasis:["source_visible","supports_target_claim"],
  reviewedAt:"2026-05-27",
  topo:{
    rel:"anchor",
    to:[Claim.System1Fast],
    strength:"strong"
  }
};

Criticism.DualProcessLimit{
  isa:Claim,
  conflictsWith:[Claim.StrongDualProcessModel],
  state:"candidate",
  topo:{
    rel:"cut",
    to:[Claim.StrongDualProcessModel],
    strength:"medium"
  }
};
```

This lets a report generator distinguish:

```text
central theory
core claims
grounding source
criticism
conflict point
final report sink
```

---

## 12) Project Mapping Use

For large projects, topology hints can produce compact structural maps.

Example project map:

```text
Project.AILO
├─ hub: Module.AILO_N
├─ bridge: Mapping.AILO_V_to_AILO_N
├─ gate: Policy.NoExecutionInsideFrame
├─ anchor: Source.DesignDecision
├─ cut: Conflict.FrameAsCommand
└─ sink: Report.AILO_Spec
```

This map is not a new syntax requirement.
It is a human-readable rendering of topology hints already present inside AILO-N frames.

---

## 13) Interaction with AILO-N Slots

### 13.1 Identity Slots

`topo` does not define identity.
Use `id`, `label`, `alias`, `isa`, `kind`, and `role` for identity.

### 13.2 Relation Slots

`topo` does not define direct relations.
Use `dependsOn`, `requires`, `governedBy`, `supports`, `blocks`, `allows`, `routesTo`, and related slots for actual relations.

### 13.3 State Slots

`topo` does not define epistemic status.
Use `state`, `conf`, `source`, `evidence`, `assertedBy`, and `assertionBasis` for status and grounding.

### 13.4 Constraint Slots

`topo` does not replace constraints.
Use `must`, `cannot`, `should`, `scope`, `risk`, `rule`, `validWhen`, and `invalidWhen` for constraints.

### 13.5 Summary

```text
identity slots = what the frame is
relation slots = how the frame relates
evidence/state slots = how the frame is grounded
topo = what structural function the frame performs in the relation network
```

---

## 14) Recommended Canonical Addition

Add one optional slot to the AILO-N canonical surface:

```ailo
topo,
```

Recommended location:

```ailo
scope,
risk,
rule,
topo,
validWhen,
invalidWhen,
```

Rationale:

`topo` is closer to usage boundary, relation structure, routing, compression, and validation than to identity or content.

---

## 15) Validation Notes

Recommended warnings:

| Code | Meaning | Action |
|---|---|---|
| T001 | unknown `topo.rel` value | warn or ignore |
| T002 | `topo.to` references undefined frame | warn or reject by profile |
| T003 | hard `gate` without rule or condition | warn |
| T004 | hard `cut` without conflict, block, or cannot relation | warn |
| T005 | `anchor` without source or evidence | warn |
| T006 | `sink` without produces, contains, stores, or output relation | warn |
| T007 | topology hint conflicts with relation slots | warn or reject by profile |

Topology validation should remain light.
The pack should not make ordinary AILO-N frames invalid unless a strict profile is enabled.

---

## 16) Minimal Working Example

```ailo
Book.Target{
  isa:Book,
  title:"Sample Book",
  state:"observed",
  source:[Source.UserInput],
  topo:{rel:"hub", strength:"medium"}
};

Claim.Core{
  isa:Claim,
  subject:Book.Target,
  predicate:"argues",
  object:Concept.MainThesis,
  evidence:[Source.PrimaryText],
  state:"candidate",
  conf:0.76,
  topo:{
    rel:"hub",
    to:[Book.Target, Source.PrimaryText, Report.BookResearch],
    strength:"strong"
  }
};

Source.PrimaryText{
  isa:Source,
  supports:[Claim.Core],
  state:"asserted",
  source:[Source.PrimaryText],
  evidence:[Evidence.DirectReference],
  assertedBy:Validator.SourceCheck,
  assertionBasis:["primary_source_visible","supports_target_claim"],
  reviewedAt:"2026-05-27",
  topo:{
    rel:"anchor",
    to:[Claim.Core],
    strength:"strong"
  }
};

Policy.EvidenceRequired{
  isa:Policy,
  blocks:[Action.AssertWithoutEvidence],
  allows:[Action.PromoteWithEvidence],
  state:"asserted",
  source:[Source.PolicyNote],
  evidence:[Rule.EvidenceRequired],
  assertedBy:Validator.PolicyCheck,
  assertionBasis:["source_visible","promotion_gate_defined"],
  reviewedAt:"2026-05-27",
  topo:{
    rel:"gate",
    to:[State.Candidate, State.Asserted],
    strength:"hard"
  }
};

Report.BookResearch{
  isa:Report,
  contains:[Book.Target, Claim.Core, Source.PrimaryText],
  state:"candidate",
  topo:{
    rel:"sink",
    to:[Book.Target, Claim.Core, Source.PrimaryText],
    strength:"strong"
  }
};

verify{
  obj:Claim.Core,
  rule:{check:["anchor_exists","gate_passed","no_hard_cut"]},
  to:Verdict.ClaimCore
}!

compress{
  obj:[Book.Target, Claim.Core, Source.PrimaryText, Policy.EvidenceRequired, Report.BookResearch],
  rule:{preserve_topo:["hub","anchor","gate","sink"], budget:"900tokens"},
  to:Context.BookResearchPacket
}!
```

---

## 17) Operational Guidance

Use `topo` when:

- a frame participates in a complex relation network
- compression needs a structural priority signal
- validation depends on gates, cuts, or anchors
- a report, artifact, or memory record collects many frames
- a frame connects two modules, domains, or stages
- project continuity depends on relation structure
- creative continuity requires stable motif, character, or theme relations

Avoid `topo` when:

- the frame is simple and single-use
- ordinary relation slots are enough
- no routing, validation, compression, or memory benefit exists
- the topology label would only duplicate the frame's identity
- the topology label is speculative and not useful for downstream work

---

## 18) Summary

AILO Relation Topology Pack adds one optional hint slot to AILO-N:

```ailo
topo:{rel,to,strength}
```

It marks the structural function of a frame in its surrounding relation network.

Core relation topology values:

```text
hub
chain
bridge
gate
loop
cut
anchor
sink
```

`topo` does not replace relation slots.
It does not create a new AILO layer.
It does not execute actions.

It helps with:

```text
relation mapping
context compression
validation planning
engine routing
memory prioritization
project mapping
creative continuity
research structure analysis
```

Final principle:

```text
AILO-N defines frames.
AILO-V acts on frames.
Relation topology helps preserve the structural function of frames inside a relation network.
```

