# CANON_STATUS

This file separates current canon, active references, legacy lineage, experimental materials, and externalized packages.

The goal is not to delete old work. The goal is to prevent readers from treating every historical file as equally current.

## Status Labels

| Label | Meaning |
|---|---|
| active-canon | current official reference for this repository |
| active-reference | useful and maintained enough to use, but not the top canon |
| lineage | historical design lineage; read for context, not default operation |
| experimental | workshop or proposal material |
| externalized | maintained in another repository/package; not part of this repo's source tree |
| duplicate-review | duplicate or near-duplicate content that needs later consolidation |

## Active Canon

| Surface | Status | Read When |
|---|---|---|
| `README.md` | active-canon | entering the repo |
| `PROJECT_MAP.md` | active-canon | choosing what to read |
| `CANON_STATUS.md` | active-canon | resolving current vs legacy status |
| `docs/AILO-N/AILO_N_ASSET_FRAME_USE_CARD_v0_1.md` | active-canon | applying AILO-N to reusable targets/assets |
| `docs/AILO-N/AILO-N_Nominal_Frame_Layer_v0.9N.md` | active-canon | canonical AILO-N slot/state/relation/validation questions |

## Active References

| Surface | Status | Notes |
|---|---|---|
| `AILO FULL STACK/FULL STACK README.md` | active-reference | v0.9E++ full-stack package entry |
| `AILO FULL STACK/AILO Full‑Stack v0.9E++ — Unified Core + Knowledge Pack (Final, MIT).md` | active-reference | full-stack lineage and operational grammar reference |
| `AILO–MCP Bridge/README.md` | active-reference | MCP bridge entry |
| `AILO–MCP Bridge/AILO–MCP Bridge v1.0 LTS.md` | active-reference | bridge package spec |
| `Logic Extension/README.md` | active-reference | logic extension entry |
| `IVK-SEAL/README.md` | active-reference | IVK/SEAL entry |
| `AILO–Search Cognitive Integration/README.md` | active-reference | search/cognitive integration entry |

## Legacy / Lineage

| Surface | Status | Notes |
|---|---|---|
| `AILO (AI Language Object) v0.9.md` | lineage | original AILO v0.9 line |
| `AILO Manifesto v0.9 — Language of Intelligence.md` | lineage | manifesto framing |
| `AILO Cognitive Architecture Proposal.md` | lineage | architecture proposal |
| `AILO–SCP Unified Specification v0.9-E.md` | lineage | SCP-era specification |
| `AILO–SCP Unified Specification v0.9E+ (Nuance Edition).md` | lineage | nuance edition lineage |
| `AILO–SCP Unified Master Specification v0.9-E (End Edition).md` | lineage | previous root README topic |
| `docs/legacy/README_legacy_v0.9E_End_Edition.md` | lineage | preserved former README content |

## Externalized Packages

| Package | Status | Notes |
|---|---|---|
| Jarvis Starter Pack | externalized | maintained as a separate repository/package |
| `docs/separate-repositories/JARVIS_STARTER_PACK.md` | active-reference | local pointer explaining the split |

## Prompts

| Surface | Status | Notes |
|---|---|---|
| `prompts/` | active-reference | ready-to-use prompt variants; review individually before treating as canon |

## Experimental

| Surface | Status | Notes |
|---|---|---|
| `Workshop/` | experimental | promotion candidates only after review |
| `TSX/` | experimental | studio/projection-language materials |

## Compatibility Pointers

| Pointer | Canonical Target | Reason |
|---|---|---|
| `AILO–Search Cognitive Integration/AILO-SEARCH for GPT.md` | `prompts/AILO-SEARCH.md` | preserve older package-local links while keeping one prompt body |

## Public Hygiene Queue

Before a public release pass:
- add redirects before moving or renaming public files
- avoid breaking existing external links until a migration note exists
- keep runnable starter packages out of this repository unless a file is intentionally promoted into AILO canon
- normalize folder and file naming only after public links are checked

## One-Line Rule

Current canon is routed by `README.md`, `PROJECT_MAP.md`, `CANON_STATUS.md`, and `docs/AILO-N/`; older files remain valuable lineage, not default entry points.