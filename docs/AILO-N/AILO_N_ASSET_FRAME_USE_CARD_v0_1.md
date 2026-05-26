# AILO-N Asset Frame Use Card v0.1

## Purpose

This card is the short operational surface for using AILO-N inside the AI Language Object repository.

It is not the v3 Starter card.
It is for framing repeated local assets, design sources, prompt packages, brains, rules, wiki notes, verification targets, and source candidates as reusable noun-slot frames.

Official source authority:

```text
docs/AILO-N/AILO-N_Nominal_Frame_Layer_v0.9N.md
```

Source provenance:

```text
internal source snapshot promoted into this repository as docs/AILO-N/AILO-N_Nominal_Frame_Layer_v0.9N.md
```

Do not read the full source by default. Use this card first when a reusable target needs a stable object frame.

## One-Line Definition

```text
AILO-N gives repeated targets a stable noun-slot frame so AILO verbs, function packs, design grammar, verification, and memory surfaces can act on the same object without re-explaining it.
```

## Local Relationship

```text
design grammar
-> locks the design shape

AILO-V / intent
-> performs query, report, execute, promote, verify, compress

AILO-N
-> names and stabilizes the reusable target

AILO function / function pack
-> controls repeated work movement around that target

adjacent internal layers
-> meaning, axis, relation, conflict, and causality support

Canon / wiki / memory surfaces
-> decide what remains reusable later
```

AILO-N does not replace AILO verbs, function packs, engines, skills, brains, wiki, or memory. It gives them stable targets.

## Use When

Use AILO-N when:

```text
repeated_target:true
asset_path_or_identity_must_stay_visible:true
relation_direction_must_be_preserved:true
candidate_vs_asserted_state_must_be_visible:true
source_evidence_assertion_basis_must_be_visible:true
context_packet_needed:true
```

Typical local targets:

```text
Brain.VerificationRuntime
Spec.AILO_N
FunctionPack.PrecheckControl
Policy.LocalRulebook
Route.DesignProductionMap
WikiNote.ReusableRule
Source.GarasaniOmega
PromptPackage.InformationDesignGPT
Report.ValidationSummary
Project.StarterFSystem
Codebase.TargetRepo
```

## Do Not Use When

Do not use AILO-N when:

```text
single_use_simple_request:true
no_reusable_target:true
frame_would_duplicate_plain_note:true
validation_rule_missing_for_persistent_use:true
execution_intent_is_inside_noun_frame:true
the_target_is_better_as_raw_material:true
```

If a note is only a temporary thought, keep it as trace or candidate material. Do not frame it as a durable object.

## Practical Asset Frame Shape

```ailo
Frame.Name{
  isa,
  role,
  path,
  partOf,
  dependsOn,
  governedBy,
  blocks,
  validates,
  useFor,
  readWhen,
  doNotReadWhen,
  source,
  evidence,
  state,
  conf,
  assertedBy,
  assertionBasis,
  reviewedAt,
  trace
};
```

This is a local practical shape, not the full canonical source.

Profile-bound local extension slots:

```text
path
-> local or relative asset path

readWhen
-> when this frame should be opened

doNotReadWhen
-> when this frame should not be opened

owner
-> responsible brain, process, or operator

route
-> entry path or route surface
```

## Compressed Frame Shape

Use only for boot summaries, route maps, and short context packets.

```ailo
Frame.Name{
  isa,
  role,
  path,
  state
};
```

Do not use compressed shape for promotion, validation, canon memory, or source claims.

## State Rules

```text
observed
-> extracted or seen from input

candidate
-> proposed but not verified

asserted
-> accepted for the current system context through visible basis

inferred
-> derived by a rule, graph, or controlled reasoning process

deprecated
-> retained but no longer recommended

rejected
-> failed validation
```

Promotion rule:

```text
candidate -> asserted
only when source/evidence/assertedBy/assertionBasis/reviewedAt are visible
```

Required for asserted:

```text
source
evidence
assertedBy
assertionBasis
reviewedAt
```

Confidence is only a helper hint. It cannot promote a frame.

## Validation Gates

Reject, stop, or keep as candidate when:

```text
missing_isa
undefined_target
slot_type_mismatch
relation_domain_mismatch
relation_range_mismatch
asserted_without_source_or_assertion_basis
candidate_used_as_fact
execution_instruction_inside_noun_frame
invalid_state_transition
formal_source_conflict
path_or_identity_unclear
read_route_missing
```

## Correct Verb Separation

Wrong:

```ailo
Spec.AILO_N{
  isa:Spec,
  verify:true
};
```

Right:

```ailo
Spec.AILO_N{
  isa:Spec,
  role:"nominal_frame_layer",
  path:"docs/AILO-N/AILO-N_Nominal_Frame_Layer_v0.9N.md",
  state:"candidate"
};

verify{
  obj:Spec.AILO_N,
  rule:{check:[isa, role, path, source, assertionBasis]},
  to:"frame_verdict"
}!
```

## Local Asset Examples

### Design Source Frame

```ailo
Spec.AILO_N{
  isa:Spec,
  role:"nominal_frame_layer",
  path:"docs/AILO-N/AILO-N_Nominal_Frame_Layer_v0.9N.md",
  partOf:[System.AILO],
  useFor:[Task.TargetFraming, Task.ContextCompression],
  governedBy:[Policy.SourceReadWhenNeeded],
  source:[Source.GarasaniOmega],
  evidence:[Report.LocalReview],
  state:"asserted",
  assertedBy:CodexLibrarian,
  assertionBasis:["source_promoted","hygiene_checked","route_registered"],
  reviewedAt:"2026-05-27",
  conf:0.86
};
```

### Verification Brain Frame

```ailo
Brain.VerificationRuntime{
  isa:Brain,
  role:"purpose_aligned_verification",
  path:"<WORKSPACE_ROOT>/Verification_Brain_System",
  consumes:[Artifact.Target, Rule.AcceptanceCriteria],
  produces:[Report.Validation],
  governedBy:[Policy.EvidenceRequired],
  blocks:[Action.UnverifiedCompletion],
  validates:[Rule.AcceptanceCriteria, Report.Validation],
  state:"candidate",
  source:[Source.LocalWorkspace],
  conf:0.74
};
```

### Design Production Map Frame

```ailo
Route.DesignProductionMap{
  isa:Route,
  role:"design_production_entry_surface",
  path:"<WORKSPACE_ROOT>/prompts/.codex_librarian_brain/DESIGN_PRODUCTION_MAP.md",
  useFor:[Task.PromptProduction, Task.BrainDesign, Task.PackageDesign],
  readWhen:["new prompt package", "new brain blueprint", "design route unclear"],
  doNotReadWhen:["simple edit", "single-file rewrite"],
  state:"candidate",
  source:[Source.CodexLibrarianBrain]
};
```

## Context Packet Rule

When context is too large:

```text
frame
-> preserve only isa, role, path, critical relations, state, source, assertionBasis, conf
-> pass compact packet to AILO verb, function pack, design surface, or verification target
```

Example packet:

```text
Spec.AILO_N is a Spec.
Role: nominal_frame_layer.
Path: docs/AILO-N/AILO-N_Nominal_Frame_Layer_v0.9N.md.
Use: target framing and context compression.
State: asserted.
Basis: source_promoted, hygiene_checked, route_registered.
```

## Source Rule

The full AILO-N source is authority for:

```text
canonical slot list
relation contracts
formal mapping
state transition details
validation code details
knowledge pack shape
strict fixtures
```

This local card is enough for:

```text
asset framing
prompt package target framing
brain design target framing
wiki/canon candidate framing
verification target framing
context packet compression
quick noun-frame validation
```

## Stop Rule

Stop and open the full source only when:

```text
canonical_slot_dispute:true
relation_contract_needed:true
formal_mapping_needed:true
validation_code_detail_needed:true
knowledge_pack_shape_needed:true
strict_validator_design_needed:true
```

## One-Line Rule

```text
Use AILO-N to name, state, and ground the reusable target; use AILO verbs, function packs, design grammar, and verification to act on it.
```
