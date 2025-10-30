# 🌐 **AILO–LitTrans v0.9 — Full Spectrum Edition (Complete)**

**License:** MIT © 2025 sorihanul  
**Scope:** Literary Translation · Bilingual Reasoning · Korean Fidelity Enhancement

---

## 0) Purpose

**AILO–LitTrans v0.9 Full Spectrum Edition** integrates semantic precision, stylistic diversity, and affective nuance into a two‑phase translation‑editing pipeline.  
It preserves *meaning* and *tone* while allowing wide stylistic variance, tailored for Korean literary fidelity.  

---

## 1) System Architecture

### Two‑Phase Translation Engine

| Phase | Name | Function |
|-------|------|-----------|
| **1** | **DRAFT‑SEM** | Stable semantic skeleton (literal core, low temperature) |
| **2** | **STYLE‑RENDER** | Literary reconstruction (high temperature, stylistic genes applied) |

Each phase outputs `N` candidates; a **re‑ranking module** evaluates by semantic fidelity, affective match, Korean naturalness, and style adherence.

### Core Formula

```
FID = 0.40·SRM + 0.25·AffSRM + 0.20·KONat + 0.15·StyleAdh
```

Where:
- **SRM** – Semantic Retention Metric
- **AffSRM** – Affective Similarity
- **KONat** – Korean Naturalness (syntax, idiom, rhythm)
- **StyleAdh** – Style adherence (tone, rhythm, diction)

---

## 2) User Commands (Simplified Interface)

```
/translate
source_lang: EN
target_lang: KO
mode: literary
style: tone=서정적, rhythm=느림, recreation=0.6, metaphor=0.7,
       lexicon=native0.7/sino0.2, punctuation=서정적쉼
source_text: """
It was the kind of rain that forgot how to stop.
"""
deliverable: FINAL
```

Optional: `/compare`, `/polish ko`, `/preset save`, `/preset apply` remain available.

---

## 3) Style Gene Set (Extended)

```
style_genes = {
  tone: [서정적, 담담, 비극적, 냉랭, 격렬],
  rhythm: [짧음, 보통, 느림],
  narrative_voice: [1인칭회고, 3인칭제한, 전지적],
  lexicon_bias: {sino_kor:0.0..1.0, native_kor:0.0..1.0, archaism:0.0..1.0, modern:0.0..1.0},
  diction_register: 문어 | 중간 | 구어,
  metaphor_density: 0.0..1.0,
  line_length: 짧음 | 보통 | 김,
  punctuation: 최소 | 표준 | 서정적쉼
}
```

Default: faithful yet fluent; extremes encouraged for experimentation.

---

## 4) Korean Fidelity Layer

### Polish Rules (Internal)
1. National orthography compliance (국립국어원 경향)
2. Eliminate English‑style modifier chains
3. Smooth unnatural auxiliary patterns (“~하는 중이다” → concise form)
4. Normalize proper nouns and tone consistency
5. Regulate commas and pauses for rhythmic balance

### Lexical Weights
- 고유어 cluster → softness, rhythm, warmth
- 한자어 cluster → gravity, reflection, density
- 시적 어휘 cluster → resonance, texture, breath

Dynamic lexicon reweighting ensures **native fluency** and **aesthetic depth.**

---

## 5) Decoding Configuration

| Phase | temp | beam | top‑p | top‑k | n_best | diverse_beam |
|-------|------|------|-------|-------|--------|---------------|
| DRAFT‑SEM | 0.25 | 1 | 0.95 | 50 | 1 | — |
| STYLE‑RENDER | 0.85 | — | 0.9 | 50 | 10 | 4 |

Automatic re‑ranking ensures the best candidate per FID threshold.

---

## 6) Error & Recovery Codes

| Code | Trigger | Action |
|------|----------|--------|
| E031 | SRM < 0.95 | Regenerate semantic draft |
| E051 | Nuance loss > 0.1 | Resample lexicon |
| E052 | Tone mismatch | Reinforce tonal weights |
| E053 | Fidelity drift > 0.08 | Re‑rank or re‑decode |

---

## 7) Sample Spectrum (One Source, Five Renders)

> **EN:** *It was the kind of rain that forgot how to stop.*

| Mode | Description | Output (KO) |
|------|--------------|--------------|
| **Literal** | 직역 기조, 의미 중심 | 멈추는 법을 잊은 비였다. |
| **Balanced** | 서정·리듬 느림 | 그 비는, 멈추는 일을 까맣게 잊은 듯, 오래도록 내렸다. |
| **Localized** | 문화·정서 중심 | 비는 제 숨을 거두는 법을 잊은 것처럼, 끝을 모른 채 스며들었다. |
| **Formal‑Poetic** | 근대 문어 기조 | 그 비라 함은 멈춤의 작법을 망각한 채, 장구히도 하강하였다. |
| **Colloquial‑Modern** | 구어, 현대 감각 | 그 비, 진짜 멈추는 걸 까먹은 듯이, 지겹게도 내렸다. |

Each candidate is rated by `(SRM, AffSRM, KONat, StyleAdh)` and the best FID is selected.

---

## 8) Integration Flow

**LitTrans → SCP (optional)**  
1. Generate multi‑spectrum outputs.  
2. Select best candidate via FID scoring.  
3. Wrap into `AILO–SCP packet` for fidelity trace + signing.  

---

## 9) Example Internal Intent

```ailo
translate{
  src:EN tgt:KO mode:literary deliverable:BOTH
  style:{tone:서정적 rhythm:느림 voice:1인칭회고
         lexicon:{sino_kor:0.2 native_kor:0.7 archaism:0.1 modern:0.4}
         diction_register:중간 metaphor_density:0.6 line_length:보통 punctuation:서정적쉼}
  decoding:{n_best:10 diverse_beam:4 temp_render:0.85}
  qa:{target:{SRM:0.95 AffSRM:0.93 KONat:0.94 StyleAdh:0.90}}
  text:"It was the kind of rain that forgot how to stop."
}!
```

---

## 10) Summary

* **Two‑phase architecture** ensures semantic stability and stylistic richness.
* **N‑best re‑ranking** widens expressive range and lexical precision.
* **Korean fidelity layer** removes literal residues and awkward phrasing.
* **Automatic recovery** guarantees coherent tone and rhythm.

> **Result:** Literary translation that breathes in Korean — faithful, fluid, and alive.

---

**AILO–LitTrans v0.9 — Full Spectrum Edition**  
_“Where translation becomes creation — in harmony with truth and tone.”_
