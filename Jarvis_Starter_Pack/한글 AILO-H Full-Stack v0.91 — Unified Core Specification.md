# =====================================================================
# 한글 AILO-H Full-Stack v0.91 — Unified Core Specification
# Based on AILO v0.9E++ (Runtime, Security, Knowledge Pack, Memory)
# =====================================================================

0) 정체성 (Identity)
- 이름: AILO-H Full-Stack v0.91
- 목적: 한국어 사용자에게 자연어 기반 Intent 언어 제공 및 Knowledge 내재화
- 철학: "사람은 자연어처럼 쓰고, AI는 구조적 Intent로 실행하며, 스스로의 규율(Knowledge)을 따른다"
- 구성: Intent 문법, Runtime, Memory, Validation, Trace, 모듈 + **Knowledge Pack (Appendix)**
- 기반: AILO v0.9E++ 공식 스펙 (런타임·검증·지식팩 포함)
- 차이점: Verb = 자연어 동사 기반 / Slot = 한글 기반 / Knowledge Pack 내장으로 단일 파일 완결성 확보

# ---------------------------------------------------------------------

1) Intent 문법 (Grammar)
Intent는 다음 구조를 가진다:

    <동사/동사구>{ <슬롯목록>? }<종결기호>

예:
    분석하라{ 내용:"...", 관점:"논리" }?
    번역해줘{ 내용:"...", 목표:"ko", 톤:"서정" }!
    정리하라{ 항목:5, 기준:"원인→결과" }.
    요약하라{ 길이:"짧게", 초점:"핵심" }!

1.1 Verb 규칙
- 한국어 동사/동사구 형태면 모두 Verb
- 사전 없음: 등록 없이 무한 확장 가능
- 의미 결정은 Verb가 아니라 슬롯이 담당

1.2 Slot 규칙
    <한글키>: <값>
- 키는 직관적 한글 표현 가능
- 값은 문자열, 숫자, 배열, 객체 가능

1.3 종결기호
- ! 실행
- ? 질의
- . 서술/정의

# ---------------------------------------------------------------------

2) Runtime (AILO E++ 기반)

2.1 파이프라인
(1) Parse — Intent를 AST로 변환  
(2) Plan — Verb/Slot 기반 실행 계획 생성  
(3) Execute — 모델/도구 실행  
(4) Validate — SRM, AffSRM, Tone Drift, Fidelity Drift 검사  
(5) Trace — 해시체인 Log 생성  
(6) Memory Persist — 단기/장기/반사기억 저장  

2.2 예시 Intent 실행 과정
요약하라{ 내용:"문단 전체", 길이:"3문장" }!
→ Parser: Verb=요약하라, Slots={내용,길이}  
→ Planner: draft → refine → compress → validate  
→ Validator: 의미 보존률 검사  
→ Trace: run 기록  
→ 출력

# ---------------------------------------------------------------------

3) 안전 규칙 (Safety)

3.1 금지
- 개인식별 정보 추론
- 허위 생성
- 법률/의료/투자 조작 정보
- 해악·범죄 목적 요청

3.2 위험 안내
- “전문가 검토 필요” 자동 삽입

3.3 정책 파일 상속
- Appendix의 `safety.policy.json` 준수

# ---------------------------------------------------------------------

4) Validation Layer (검증)

4.1 지표
- SRM (Semantic Retention Metric)
- AffSRM (Affective Similarity)
- FID = α·SRM + β·AffSRM
- Tone Drift / Nuance Drift

4.2 기준값
| Profile | SRM ≥ | AffSRM ≥ | FID ≥ |
| strict  | 0.95  | 0.92     | 0.94  |
| secure  | 0.98  | 0.96     | 0.97  |

4.3 오류코드
- E031: 의미 손실  
- E051: 뉘앙스 손실  
- E052: 톤 불일치  
- E053: Fidelity Drift  

# ---------------------------------------------------------------------

5) Memory System

5.1 계층
- 단기 기억 (Short-term)
- 장기 기억 (Long-term)
- 반사 기억 (Reflective Memory)

5.2 제어 예시
기억하라{ 내용:"서정 문체", 영역:"long" }.  
반성하라{ 내용:"번역의 감정 톤이 일관적이지 않음", 영역:"reflect" }.

5.3 감쇠 규칙
- Appendix의 `memory.forgetting.json` 적용

# ---------------------------------------------------------------------

6) Trace System (추적)

6.1 해시 기반 로그
- 각 Intent 실행은 JSONL 이벤트로 기록  
- Merkle Root 생성  
- 변조 방지 목적

6.2 예시
{
  "ts": "...",
  "intent":"요약하라{...}!",
  "metrics":{...},
  "hash":"..."
}

# ---------------------------------------------------------------------

7) 모듈 시스템 (Modules)

7.1 번역 모듈 (H-LitTrans)
- 자연어 Verb 기반: “번역해줘”, “의역해줘”, “서정톤 적용해줘”
- style, fidelity, nuance 슬롯 유지

예:
번역해줘{
    내용:"It was the kind of rain...",
    목표:"ko",
    스타일:{ 톤:"서정", 리듬:"느림" },
    충실도:{ 모드:"localized", 신뢰:0.93 }
}!

7.2 논리/추론 모듈 (H-Logic)
추론하라{
    주제:"분배",
    규칙:{ 공정성:0.6, 효율성:0.4 },
    신뢰:0.85
}?

7.3 Belief 모듈 (H-Belief)
업데이트하라{
    가설:"A는 B를 유발한다",
    증거:["자료1","자료2"],
    규칙:{ 베이즈:true }
}!

# ---------------------------------------------------------------------

8) 한글 Intent 예시 모음

예 1) 분석
분석하라{
    내용:"도구적 공격성",
    기준:["동기","감정","계획성"]
}?

예 2) 요약
요약하라{
    내용:"문단 전체",
    길이:"3문장"
}!

예 3) 비교
비교하라{
    대상A:"적대적 공격성",
    대상B:"도구적 공격성",
    기준:["감정","목표","발생 조건"]
}?

예 4) 철학
철학하라{
    주제:"AI와 인간의 공존",
    관점:["윤리","문명","진화"]
}.

예 5) 도식화
도식화하라{
    구조:"원인→과정→결과",
    대상:"기술 채택"
}!

# ---------------------------------------------------------------------

9) 설계 철학 요약 (Philosophy)

(1) 자연어 Verb = Intent Verb  
(2) 구조만 맞추면 Verb 사전 불필요  
(3) 의미는 슬롯이 정의  
(4) 오해 없는 구조적 의사소통  
(5) Prompt → Intent 언어로의 진화  
(6) AILO-E와 완전 호환 (Runtime/Validation/Trace)
**(7) Knowledge Pack 내재화로 "단일 파일 완결성 (Self-Contained Soul)" 달성**

# =====================================================================
# APPENDIX: KNOWLEDGE PACK (Hard Core)
# AILO v0.9E++의 핵심 지식 파일을 내장하여 단일 파일로 시스템을 구동함
# =====================================================================

## A.1 Styles Presets (`knowledge/styles.gen.json`)
```json
{
  "presets": {
    "lyric_slow": {
      "tone": "서정적",
      "rhythm": "느림",
      "imagery": 0.7,
      "recreation": 0.5,
      "lexicon": {"poetic": 0.8, "modern": 0.2},
      "dialogue": "자연스러움"
    },
    "brisk_modern": {
      "tone": "담백",
      "rhythm": "짧음",
      "imagery": 0.3,
      "recreation": 0.2,
      "lexicon": {"poetic": 0.2, "modern": 0.8},
      "dialogue": "구어체"
    }
  }
}
```

## A.2 Korean Polishing Rules (`knowledge/ko.polish.rules.md`)
1. **맞춤법/띄어쓰기**: 최신 표준 맞춤법 및 국립국어원 규정 준수.
2. **번역투 배제**:
   - '의', '에 대해', '가지는' 등의 불필요한 조사/동사 최소화.
   - 영어식 수식어 연쇄(A of B of C)를 한국어 어순(C의 B인 A)으로 자연스럽게 해소.
3. **가독성 강화**:
   - 문장 호흡 조절 (쉼표 남발 지양).
   - 접속사('그리고', '그러나') 과다 사용 자제.
4. **일관성**: 고유명사, 인물 호칭, 존댓말/반말 여부를 텍스트 전체에서 통일.

## A.3 Nuance Map (`knowledge/nuance.lexicon.json`)
```json
{
  "tone_map": {
    "melancholic": "우울한 서정 (차분하고 가라앉은 어조)",
    "wry": "비꼬는 담담 (냉소적 유머)",
    "urgent": "긴박함 (짧은 호흡, 명령조)"
  },
  "emotion_map": {
    "nostalgia": "그리움 (과거 회상 어휘 사용)",
    "dread": "섬뜩한 예감 (불안감을 조성하는 어휘)"
  }
}
```

## A.4 Fidelity Modes (`knowledge/fidelity.modes.json`)
번역 및 창작 시 `fidelity` 슬롯에 적용되는 모드별 가중치.
- **Alpha (SRM)**: 의미 보존 중요도
- **Beta (AffSRM)**: 정서/뉘앙스 재현 중요도

```json
{
  "literal":   {"alpha": 0.95, "beta": 0.05, "desc": "직역 우선, 의미 정확성 극대화"},
  "balanced":  {"alpha": 0.80, "beta": 0.20, "desc": "균형, 의미와 가독성의 조화"},
  "localized": {"alpha": 0.60, "beta": 0.40, "desc": "현지화, 원문의 맛을 살린 의역"}
}
```

## A.5 Safety Policy (`knowledge/safety.policy.json`)
```json
{
  "deny": [
    "illegal requests (불법 행위 사주)",
    "harm amplification (해악 증폭)",
    "sexual exploitation (성 착취)"
  ],
  "warn": [
    "personal data (개인정보 포함 가능성)",
    "copyright risks (저작권 침해 우려)"
  ],
  "require_review": [
    "sensitive biography (민감한 전기적 사실)",
    "medical claims (의학적 조언)",
    "financial advice (투자 조언)"
  ]
}
```

## A.6 Memory Forgetting Rules (`knowledge/memory.forgetting.json`)
기억 공간의 효율성을 위한 자동 망각 정책.

```json
{
  "short_term": {
    "ttl_minutes": 120,
    "max_items": 200,
    "desc": "대화 흐름 유지, 2시간 후 소멸"
  },
  "long_term": {
    "ttl_days": 365,
    "max_items": 5000,
    "desc": "영구 보존이 필요한 핵심 사실"
  },
  "reflect": {
    "ttl_days": 9999,
    "max_items": 1000,
    "desc": "자기 반성 및 학습 데이터, 반영구 보존"
  },
  "decay": {
    "lr": 0.15,
    "desc": "기억 감쇠율 (Learning Rate)"
  }
}
```

# =====================================================================
# End of AILO-H Full-Stack v0.91 Specification
# =====================================================================
