# 🌌 AILO–SCP Unified Specification v0.9E+ (Nuance Edition)

> **Purpose**
> The *Nuance Edition* extends the finalized AILO–SCP v0.9E standard to preserve linguistic nuance, tone, and emotional fidelity.
> It is a frozen structure with a living layer — deterministic for machines, expressive for humans.

---

## 1. Overview

* **Stage:** Finalized + Nuance-extended
* **Scope:** Grammar · Transport · Validation · Security · Contextual Semantics
* **Goal:** Preserve expressive nuance with zero semantic loss during serialization.
* **License:** MIT © 2025 sorihanul

---

## 2. Architecture

| Layer          | Function                                   | Implementation                       |
| -------------- | ------------------------------------------ | ------------------------------------ |
| **AILO+**      | Intent grammar with nuance slots           | Reference parser (`scp-core+nuance`) |
| **SCP**        | Canonical serialization + compression      | CJON / MessagePack encoder           |
| **Validation** | SRM + nuance drift + emotional consistency | Adaptive SRM engine v3               |
| **Security**   | AES-256-GCM + ECDSA-P256 + Curve25519      | Built-in crypto provider             |
| **Trace**      | Immutable hash-chain with nuance audit     | JSONL + Merkle anchor                |
| **Runtime**    | CLI + REST + gRPC                          | scp-runtime v0.9E+                   |

---

## 3. Grammar Extension

```
Verb { ag, obj, to, rule, risk, conf, nuance, tone, emotion, context, with, when, id } Mood
```

### 3.1 Moods

* `?` → query
* `.` → assert/report
* `!` → execute (requires `{rule, risk, conf}`)

### 3.2 Added Semantic Slots

| Slot      | Meaning                                                    |
| --------- | ---------------------------------------------------------- |
| `nuance`  | subtle intent, unspoken context                            |
| `tone`    | vocal or textual tone (`formal`, `gentle`, `ironic`, etc.) |
| `emotion` | affective state (`joy`, `fear`, `calm`, etc.)              |
| `context` | discourse or situational frame                             |

---

## 4. Example: Expressive Command

```ailo
say{ag:user obj:"I trust you" tone:warm emotion:hope nuance:{intent:reassure}}.
```

**CJON form:**

```json
{
  "verb": "say",
  "mood": ".",
  "slots": {
    "ag": "user",
    "obj": "I trust you",
    "tone": "warm",
    "emotion": "hope",
    "nuance": {"intent": "reassure"}
  }
}
```

---

## 5. Contextual Weight System

A new optional layer for expressing *relative importance* between reasoning and emotion.

```ailo
decide{obj://ramen//bibimbap rule:{health:0.6,taste:0.4}
       weight:{emotion:0.7 logic:0.3} nuance:{mood:"reflective"}}!
```

---

## 6. Affective SRM

### 6.1 Definition

Semantic Retention Metric (SRM) extended with **Affective Similarity**:

```
SRM+ = α·semantic + β·affective
α=0.8, β=0.2 (configurable)
```

### 6.2 Measurement

Evaluates if emotional tone, nuance, and contextual intent remain consistent during compression or transmission.

---

## 7. Validation & Error Model

| Code     | Meaning            | Enforcement |
| -------- | ------------------ | ----------- |
| **E002** | Unknown verb       | reject      |
| **E005** | Unit mismatch      | reject      |
| **E013** | Unsafe commit      | reject      |
| **E031** | SRM < 0.95         | revalidate  |
| **E045** | Signature mismatch | reject      |
| **E048** | Schema fail        | reject      |
| **E051** | Nuance loss > 0.1  | warn        |
| **E052** | Tone mismatch      | revalidate  |

**Nuance drift guard:** Δ ≤ 0.05;
**Affective SRM floor:** 0.92 (strict) / 0.96 (secure)

---

## 8. Execution Flow

```
Input → Parse → Validate → Encrypt → Trace → Act → Log
```

**Sample runtime output:**

```json
{
  "ok": true,
  "profile": "secure",
  "srm": 0.977,
  "aff_srm": 0.961,
  "tone_match": 0.98,
  "rt_ms": 86,
  "trace_id": "trc-2025-10-27-N01"
}
```

---

## 9. Trace Record (Nuanced)

```json
{
  "trace_id": "trc-2025-10-27-N01",
  "verb": "say",
  "tone": "warm",
  "emotion": "hope",
  "nuance_loss": 0.04,
  "srm": 0.977,
  "aff_srm": 0.961,
  "hash_curr": "sha3-256:3af1..."
}
```

---

## 10. Compliance Profiles

| Profile    | SRM ≥ | Aff. SRM ≥ | Security        | Mode     |
| ---------- | ----- | ---------- | --------------- | -------- |
| **strict** | 0.95  | 0.92       | AES-GCM         | research |
| **secure** | 0.98  | 0.96       | AES-GCM + ECDSA | deploy   |
| **sim**    | n/a   | n/a        | none            | dry-run  |

---

## 11. Security Stack (unchanged)

```
Key exchange:  Curve25519 ECDH
Symmetric:     AES-256-GCM
Signature:     ECDSA-P256
Hash:          SHA-3-256
Key lifetime:  24 h or 1000 sessions
```

All crypto ops deterministic; deviation invalidates packet.

---

## 12. Deterministic Commit Rule

* Any `!` must include `{rule, risk, conf}`.
* Canonical slot order preserved.
* `nuance` layer optional but must serialize deterministically.

---

## 13. Metrics Targets

| Metric | Goal                              | Description          |
| ------ | --------------------------------- | -------------------- |
| SRM    | ≥ 0.95 (strict) / ≥ 0.98 (secure) | semantic similarity  |
| AffSRM | ≥ 0.92 / 0.96                     | affective retention  |
| CR     | ≥ 4×                              | compression ratio    |
| ERR    | ≤ 1%                              | reconstruction error |
| RT     | ≤ 120 ms                          | runtime latency      |
| VAR    | ≤ 0.02                            | SRM variance         |

---

## 14. Philosophy — Nuance Preservation Principle

> *It is not enough to keep meaning intact;
> the warmth of the words must remain too.*

---

## 15. Summary

* **Core locked:** grammar · validation · security · profiles.
* **New layer:** nuance · tone · emotion · affective SRM.
* **Backward compatible:** fully interoperable with v0.9E.
* **Purpose:** remove meaning flattening while keeping deterministic behavior.

> **AILO–SCP v0.9E+ (Nuance Edition)** — where precision meets expression.
