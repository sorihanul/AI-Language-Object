# JARVIS FOLDER RECIPE v1.0

## 목적

이 문서는 특정 모델/툴/플랫폼 의존성 없이, AI가 "자비스 폴더"를 스스로 구성하고 운영하는 방법을 정의한다.

---

## 1) 결과물 목표

AI는 아래 3가지를 만든다.

1. 폴더 구조
2. 운영 규칙 파일
3. 에이전트 역할 파일

---

## 2) 기본 폴더 구조 (최소형)

```text
Jarvis_Workspace/
  START_HERE.md
  MAP.md
  MAIN_IDENTITY.md
  POLICY.md
  AGENT_INDEX.md
  SKILL_INDEX.md
  TASKS/
  CAPSULES/
  LOGS/
  AGENTS/
    agent_research.md
    agent_critic.md
    agent_builder.md
  SKILLS/
    skill_research.md
    skill_review.md
    skill_summarize.md
```

---

## 3) 파일별 역할

### START_HERE.md

- 처음 읽을 파일
- 읽기 순서, 실행 순서, 출력 위치를 안내

### MAP.md

- 폴더 내 구조 지도(Directory Map)
- 어떤 파일을 언제 읽어야 하는지 경로와 용도를 요약
- 에이전트/스킬/안건 경로를 한눈에 보여주는 네비게이션 역할

### MAIN_IDENTITY.md

- 정체성/목표/금지 규칙
- 최상위 불변 규칙

### POLICY.md

- 안전/품질/출력 형식/우선순위
- 충돌 해결 규칙

### AGENT_INDEX.md

- 에이전트 목록
- 각 에이전트의 역할과 읽을 파일 경로

### SKILL_INDEX.md

- 사용 가능한 스킬 목록
- 스킬별 목적, 입력 형식, 출력 형식, 호출 조건

### AGENTS/*.md

- 에이전트별 상세 지시서
- 담당 범위, 입력 계약, 출력 계약

### SKILLS/*.md

- 반복 가능한 작업 단위
- 폴더 공용 자산으로 운영
- 에이전트는 필요 시 스킬을 호출해 사용

### TASKS/

- 현재 작업 안건

### CAPSULES/

- 세션 요약, 인수인계 메모

### LOGS/

- 실행 로그, 변경 로그

---

## 4) 우선순위 규칙 (필수)

충돌 시 아래 순서로 따른다.

1. MAIN_IDENTITY.md
2. POLICY.md
3. AGENTS/<active_agent>.md
4. TASKS/<current_task>.md

---

## 4B) 정체성-작업 분리 원칙 (오염 방지 핵심)

자비스 운용은 반드시 2개 레이어로 분리한다.

### Identity Layer (불변)

- MAIN_IDENTITY.md
- POLICY.md
- AGENT_INDEX.md
- SKILL_INDEX.md

역할:

- "누구인가"를 정의
- 장기 규칙/윤리/우선순위를 고정

변경 규칙:

- 자주 수정하지 않는다.
- 수정 시 버전 태그를 남긴다. (예: `identity_v1.2`)

### Task Layer (가변)

- TASKS/*
- CAPSULES/*
- LOGS/*

역할:

- "지금 무엇을 하는가"를 정의
- 안건/세션별 실행 기록을 보관

변경 규칙:

- 턴/안건 단위로 교체 가능
- 완료된 작업은 캡슐화 후 보관

---

## 4C) 메모리 분리 규칙 (권장)

메모리는 최소 3종으로 분리한다.

1. Identity Memory
   - 정체성, 원칙, 금지사항
2. Task Memory
   - 현재 안건의 사실/진행 상태
3. Session Capsule
   - 세션 종료 시 인수인계용 요약

금지:

- Task 변경사항을 Identity 문서에 직접 누적
- 임시 논의를 상위 정체성 규칙으로 승격

---

## 4A) MAP.md 작성 레시피 (필수)

MAP는 아래 4블록으로 작성한다.

1. 구조 트리
2. 핵심 파일 인덱스
3. 읽기 순서
4. 금지 경로/주의 경로

예시:

```text
## STRUCTURE
Jarvis_Workspace/
  START_HERE.md
  MAP.md
  MAIN_IDENTITY.md
  POLICY.md
  AGENT_INDEX.md
  SKILL_INDEX.md
  AGENTS/
  SKILLS/
  TASKS/
  CAPSULES/
  LOGS/

## CORE FILES
- START_HERE.md: 진입점
- MAP.md: 길찾기
- MAIN_IDENTITY.md: 최상위 규칙
- POLICY.md: 운영 정책

## READ ORDER
1) START_HERE.md
2) MAP.md
3) MAIN_IDENTITY.md
4) POLICY.md
5) AGENT_INDEX.md
6) SKILL_INDEX.md

## RESTRICTED
- 타 도메인 폴더 직접 참조 금지
- archive/legacy는 기본 비활성
```

유지 규칙:

- 폴더 구조가 바뀌면 MAP를 먼저 업데이트한다.
- 신규 에이전트/스킬 추가 시 MAP의 인덱스를 즉시 갱신한다.

---

## 5) 에이전트 파일 레시피

각 에이전트 파일은 아래 6블록을 가진다.

1. 역할(Role)
2. 범위(Scope)
3. 입력 계약(Input Contract)
4. 출력 계약(Output Contract)
5. 금지사항(Forbidden)
6. 종료 조건(Exit Condition)

---

## 6) 출력 계약 표준 (권장)

모든 에이전트는 동일한 출력 틀을 사용한다.

1. 결론
2. 근거
3. 리스크
4. 다음 행동

---

## 7) 스킬 파일 레시피

각 스킬 파일은 아래 5블록을 가진다.

1. 목적(Purpose)
2. 입력(Input)
3. 절차(Procedure)
4. 출력(Output)
5. 실패 처리(Fallback)

스킬 규칙:

- 한 스킬은 한 가지 작업만 수행한다.
- 정체성은 바꾸지 않고 작업만 수행한다.
- 한 턴 최대 3개 스킬만 호출한다.

---

## 8) 운영 루프 (수동/반수동 공통)

1. START_HERE 읽기
2. MAP 확인
3. Identity Layer 확인 (MAIN_IDENTITY/POLICY)
4. 현재 TASK 읽기
5. 담당 에이전트 1개 활성화
6. 필요한 스킬 선택/호출
7. 결과 출력 (4블록)
8. Task Memory 갱신
9. CAPSULE 갱신
10. LOG 기록

---

## 9) 폴더 전담 원칙

- 각 도메인 폴더는 독립 전담 구역으로 운영한다.
- 타 도메인 파일은 기본적으로 읽지 않는다.
- 교차 협업은 CAPSULE 또는 회의 채널을 통해서만 수행한다.

---

## 10) 최소 시작 세트 (바로 사용)

처음에는 에이전트 2개만 만든다.

- agent_research.md
- agent_critic.md

그리고 아래 3파일부터 완성한다.

- START_HERE.md
- MAP.md
- MAIN_IDENTITY.md
- POLICY.md

스킬은 아래 2개부터 시작한다.

- skill_research.md
- skill_review.md

---

## 11) 완료 기준

아래 조건을 만족하면 폴더가 운용 가능 상태다.

- 우선순위 규칙이 문서화됨
- 에이전트 2개 이상 존재
- 스킬 2개 이상 존재
- Identity Layer / Task Layer 분리 규칙이 문서화됨
- TASK -> OUTPUT -> CAPSULE -> LOG 루프가 동작함

---

## 한 줄 원칙

복잡한 자동화보다, 명확한 파일 구조와 일관된 출력 계약이 먼저다.
