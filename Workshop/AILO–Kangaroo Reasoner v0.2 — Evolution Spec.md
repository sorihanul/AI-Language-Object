# 🦘 AILO–Kangaroo Reasoner v0.2 — Evolution Spec

**Goal:** 초등·저학년 이미지/직관형 수학 문항에서 **지각–도식–기호** 삼중 계층으로 일관된 고정밀 추론을 달성. v0.1을 기반으로 **데이터 스키마 정교화, 반례생성기 고도화, 라우팅 메타-컨트롤**, **훈련 커리큘럼 설계**, **SDK I/O 계약**을 확정.

---

## 0) System Topology

```
[Ingest] → [VP: Visual Parser] → SG
           [CSL: Cognitive Schema Layer] → CG
SG + CG → [SP: Strategy Planner] → Plan
Plan → [SE: Symbolic Executor] → Result
Result → [VF: Verifier] → Verdict(conf)
Verdict → [EX: Explainer] → Dual explanations
All stages orchestrated by [AILO Controller]
```

---

## 1) Data Schemas (Canonical)

### 1.1 SceneGraph (SG)

```json
{
  "meta": {"problem_id": "K2021-P1", "page": 1, "item": 3},
  "nodes": [
    {"id":"s1","kind":"shape","type":"square","bbox":[x,y,w,h],"attrs":{"grid":true}},
    {"id":"l1","kind":"line","type":"fold","p1":[x,y],"p2":[x,y],"attrs":{"symmetry":true}},
    {"id":"m1","kind":"mark","type":"cut","path":[[x,y],[x,y]]},
    {"id":"t1","kind":"text","value":"몇 조각?","pos":[x,y]}
  ],
  "edges": [
    {"src":"l1","dst":"s1","rel":"bisect"},
    {"src":"m1","dst":"l1","rel":"intersect"}
  ]
}
```

### 1.2 ConceptGraph (CG)

```json
{
  "concepts": [
    {"id":"C_sym","name":"대칭","score":0.86},
    {"id":"C_split","name":"분할","score":0.78}
  ],
  "relations": [
    {"from":"C_sym","to":"C_split","type":"implies"}
  ],
  "type_guess": {"class":"Symmetric-Split","p":0.82}
}
```

### 1.3 Plan (Strategy Contract)

```json
{
  "strategy_id":"SYM-SPLIT/01",
  "steps": [
    {"op":"identify_axis","inputs":["SG:l1"],"out":"axis"},
    {"op":"count_one_side","inputs":["SG:m1","axis"],"out":"n_side"},
    {"op":"mirror_multiply","inputs":["n_side"],"out":"n_total"},
    {"op":"overlap_correction","inputs":["SG:m1","axis"],"out":"n_final"}
  ],
  "invariants": ["parity_preserved", "mirror_equivalence"],
  "answer_slot":"n_final"
}
```

### 1.4 ProofTrace

```json
{
  "trace": [
    {"step":1,"rule":"symmetry_axis","why":"fold line is axis"},
    {"step":2,"rule":"partition_count","why":"cuts partition region"},
    {"step":3,"rule":"mirror_copy","why":"symmetric duplication"},
    {"step":4,"rule":"overlap_check","why":"avoid double counting"}
  ]
}
```

---

## 2) Cognitive Schema Layer (CSL) — v0.2 Class Set

* **A. 대칭(SYM)**: 축/중앙/회전 대칭 추출, 복제 규칙
* **B. 분할(SPLIT)**: 영역 분할, 절단, 격자분할, 중복/누락 보정
* **C. 패턴(PATTERN)**: 주기/블록/차분/규칙 귀납
* **D. 보수합(COMP)**: 자리수/보수 변환/합-차 단순화
* **E. 경로(LATTICE)**: 격자 경로 DP, 금지칸, 경계조건
* **F. 타일링(TILING)**: 단위 타일 정의, 충/필 조건, 조합 배치
* **G. 수열(SEQUENCE)**: n번째 항, 생성 규칙, 검증 표본
* **H. 비교/최소최대(COMPARE)**: 도형/수량 비교, 불변량

**Routing Rule:** top-2 CSL 후보를 병렬 탐색 → 합의 실패 시 "re-map" 1회.

---

## 3) Strategy Templates — v0.2 Upgrades

* SYM-SPLIT/01: 축 검출 → 한쪽 계산 → 대칭 복제 → 중복 보정
* TILING/02: 타일 유형 분해 → 배치 가능성 검사 → 경우의수 산출
* LATTICE/03: DP 테이블 구성 → 장애물 마스킹 → 경계값 합산
* COMP/01: 보수 변환 → 자리수 단순화 → 산술 검산
* SEQ/02: 차분/주기 탐색 → 블록 규칙화 → n항 공식 → 샘플 검증
* CASE/01: 케이스 트리(짝/홀·위치·크기) → 불변량 가지치기

각 템플릿에는 `rule_id`와 반례 패턴(`anti_patterns`)을 포함.

---

## 4) Symbolic Executor (SE) — v0.2

* **Arithmetic**: 정수/유리, 자리수 규칙, 약/최대공약수
* **Combinatorics**: nCk, 중복조합, 배치/순열 제약, 작은 n 완전탐색
* **Lattice DP**: n≤40, 장애물/금지칸/특수칸(가중) 마스킹
* **Elementary Geometry**: 격자 넓이/둘레, 대칭 복제, 평면 분할 수
* **Consistency**: 범위/단위/정수성 체크, congruence quick-check

---

## 5) Verifier (VF) — Counterexample Generator v0.2

* **Local Fuzzer**: 입력 파라미터 근방 무작위 변동 → 결과 일관성 검증
* **Mirror Consistency**: 좌/우·상/하 반전 시 결과 동일성 검사
* **Parity/Modulo Invariants**: 짝/홀·mod k 보존성 검사
* **Brute-Check (small n)**: 가능한 케이스 전수 → 답 재생성 일치
* **Confidence Scoring**: rule coverage + tests passed → conf∈[0,1]

---

## 6) Explainer (Dual-Track) — v0.2 Format

```json
{
  "child": "한쪽에서 자른 조각을 세고, 접은 선을 기준으로 똑같이 생긴 조각을 한 번 더 더하면 돼요.",
  "teacher": {
    "principles": ["mirror_equivalence", "overlap_correction"],
    "justification": [
      "접힌 선은 대칭축이므로 한쪽 영역이 다른 한쪽으로 일대일 대응함",
      "교차 절단이 있을 경우 중복 계수는 포함배제 원리로 보정"
    ]
  }
}
```

---

## 7) AILO Protocol (Executable Slots)

```
sense{obj:problem id:K2021-P1 to:ingest rule:ocr+vision conf:0.92}.
parse{obj:image to:scene_graph rule:shape/mark/text hash:SG#...}.
map{obj:scene_graph to:schema_graph rule:CSL[A|B|...] conf:0.84}.
plan{obj:schema_graph to:strategy id:SYM-SPLIT/01 conf:0.83}.
prove{obj:strategy to:result rule:symbolic(dp|comb|algebra) time<=200ms}.
check{obj:result to:verdict rule:fuzzer+invariant tests>=4 conf:0.9}.
answer{obj:verdict to:explanation audience:child|teacher}.
```

---

## 8) Prompt Pack (LLM Harness)

**System Guard:**

* 자유 추측/직감 서술 금지, 모든 단계는 슬롯 채움
* 임의 재해석 금지: `hash(SG)`·`hash(Plan)` 고정

**Input Frame:**

```json
{
  "text": "정사각형 종이를 한 번 접고 한 번 자르면 몇 조각?",
  "SG": { ... },
  "CSL_candidates": ["SYM","SPLIT"],
  "Constraints": {"answer_type":"integer","bounds":[0,100]}
}
```

**Output Frame:**

```json
{
  "TypeGuess":"Symmetric-Split",
  "ConceptNodes":["대칭","분할"],
  "Strategy":{"id":"SYM-SPLIT/01","steps":[...],"invariants":[...]},
  "SE_calls":[{"fn":"mirror_multiply","args":[...]}],
  "Checks":["parity","mirror"],
  "Final":{"answer":8,"why":"mirror_equivalence"}
}
```

---

## 9) Error Taxonomy & Recovery

* **E1 라우팅오류**: CSL 오분류 → `re-map` 1회 + top-3 soft vote
* **E2 도식-장면 불일치**: SG 누락/오검출 → VP 재파싱(阈值↓) → human-in-loop
* **E3 기호오류**: SE 함수선택/오버플로 → 대체 경로(완전탐색)로 폴백
* **E4 환각설명**: ProofTrace-Rule 미참조 시 출력 차단 → 근거 슬롯 강제

---

## 10) Training Curriculum (Human-like Abstraction)

1. **Stage-1 (Visual primitives)**: 대칭축·겹침·격자·절단 라벨링
2. **Stage-2 (Schema pairs)**: SYM↔SPLIT, LATTICE↔CASE 교차 학습
3. **Stage-3 (Strategy grounding)**: 템플릿별 입출력·반례세트
4. **Stage-4 (Verification thinking)**: 반례생성·불변량 추론 습관화
5. **Stage-5 (Explanations)**: 아동/교사용 병렬 서술 미세조정

데이터는 공개 Kangaroo·MathArena 유사문항(저작권 준수) + 합성 생성.

---

## 11) SDK I/O Contracts (Type Hints)

```ts
// TypeScript-like
export type SceneGraph = { meta:{problem_id:string}, nodes:any[], edges:any[] };
export type ConceptGraph = { concepts:{id:string,name:string,score:number}[], relations:any[], type_guess:{class:string,p:number} };
export type Plan = { strategy_id:string, steps:any[], invariants:string[], answer_slot:string };
export type ProofTrace = { trace:{step:number, rule:string, why:string}[] };

export interface ReasonerAPI {
  parseImage(img:Buffer): Promise<SceneGraph>;
  inferConcepts(sg:SceneGraph): Promise<ConceptGraph>;
  planStrategy(sg:SceneGraph, cg:ConceptGraph): Promise<Plan>;
  execute(plan:Plan, sg:SceneGraph): Promise<{result:any, trace:ProofTrace}>;
  verify(result:any, sg:SceneGraph, plan:Plan): Promise<{ok:boolean, conf:number}>;
  explain(result:any, trace:ProofTrace, audience:"child"|"teacher"): Promise<string|object>;
}
```

---

## 12) Evaluation Protocol (A/B/C/D)

* **Datasets**: Kangaroo lower grades + MathArena image subset (200~400)
* **Conditions**: Baseline(CoT) / +CSL / +CSL+SE / Full(VP+CSL+SE+VF)
* **Metrics**: Accuracy, Consistency(retry stability), Groundedness, RoutingErr, Time/Item
* **Targets**: +15~25pp(acc), +30% consistency, RoutingErr ≤ 7%

---

## 13) Roadmap

* **Sprint-1 (주차 1)**: VP 최소코어, CSL 8클래스, 템플릿 3종, SE 산술/조합, VF parity/mirror
* **Sprint-2 (주차 2)**: Lattice DP, Tiling, 반례 fuzzer, EX 듀얼 템플릿
* **Sprint-3 (주차 3)**: 데이터 합성기, 커리큘럼 Stage-2~3, A/B/C/D 평가
* **Sprint-4 (주차 4)**: 오류 복구 루프, 해시 락, SDK 베타, 리포트 자동화

---

## 14) PoC Sample (Walkthrough)

**문항:** “정사각형을 한 번 접고 한 번 자르면 몇 조각?”

* SG: 축 1, 절단 1, 격자 off → 노드/엣지 위 사양 참조
* CG: {대칭:0.86, 분할:0.78} → Type:"Symmetric-Split"
* Plan: SYM-SPLIT/01
* SE: 한쪽 count=4 → mirror_multiply=8 → overlap_correction=0 → n_final=8
* VF: parity/mirror/brute(small) pass → conf=0.91
* EX: child/teacher 출력 동시 생성

---

## 15) Compliance & Safety

* 모든 설명은 ProofTrace의 규칙ID를 참조해야 하며, 미참조 시 출력 금지
* 데이터 저작권 준수(합성/공개문항만 사용), 개인정보 없음
* 결과는 정보/학습 목적. 행동형 조언 금지

---

## 16) Deliverables (v0.2)

1. Canonical JSON 스키마(이 문서의 §1 그대로)
2. 템플릿 카탈로그 v0.2 (rule_id/anti_patterns 포함)
3. SDK 인터페이스(§11) + Mock 구현 가이드
4. 평가 하네스 스펙(§12) + 리포트 포맷
5. 커리큘럼 스테이지 설계(§10)

— End of v0.2 —

---

## 17) Sprint‑1 Implementation Skeleton (TypeScript · Mock)

> 목적: 빠른 PoC를 위한 **런닝 골격** 제공. 실제 비전/LLM 대신 규칙 기반 목업으로 파이프라인 검증.

```ts
// 17.1 Types (re‑use §11)
import type { SceneGraph, ConceptGraph, Plan, ProofTrace, ReasonerAPI } from "./types";

// 17.2 Visual Parser (Mock)
export const parseImageMock = async (png: Buffer): Promise<SceneGraph> => ({
  meta:{ problem_id:"DEMO-P1" },
  nodes:[
    { id:"s1", kind:"shape", type:"square", bbox:[10,10,100,100], attrs:{ grid:false } },
    { id:"l1", kind:"line", type:"fold", p1:[10,60], p2:[110,60], attrs:{ symmetry:true } },
    { id:"m1", kind:"mark", type:"cut", path:[[10,30],[110,30]] }
  ],
  edges:[ { src:"l1", dst:"s1", rel:"bisect" }, { src:"m1", dst:"s1", rel:"cross" } ]
});

// 17.3 CSL Heuristic Router (Mock)
export const inferConceptsMock = async (sg: SceneGraph): Promise<ConceptGraph> => {
  const hasAxis = sg.nodes.some(n => n.kind==="line" && n.type==="fold");
  const hasCut  = sg.nodes.some(n => n.kind==="mark" && n.type==="cut");
  return {
    concepts:[
      ...(hasAxis? [{id:"C_sym", name:"대칭", score:0.86}] : []),
      ...(hasCut ? [{id:"C_split", name:"분할", score:0.78}] : [])
    ],
    relations: hasAxis && hasCut ? [{from:"C_sym", to:"C_split", type:"implies"}] : [],
    type_guess: { class: hasAxis && hasCut ? "Symmetric-Split" : "Unknown", p: 0.82 }
  };
};

// 17.4 Strategy Planner (Rule Map)
const STRATEGY_MAP = {
  "Symmetric-Split": "SYM-SPLIT/01",
  // more: LATTICE/03, COMP/01 ...
} as const;

export const planStrategyMock = async (sg: SceneGraph, cg: ConceptGraph): Promise<Plan> => {
  const cls = cg.type_guess.class as keyof typeof STRATEGY_MAP;
  const id = STRATEGY_MAP[cls] ?? "CASE/01";
  return {
    strategy_id: id,
    steps:[
      { op:"identify_axis", inputs:["SG:l1"], out:"axis" },
      { op:"count_one_side", inputs:["SG:m1","axis"], out:"n_side" },
      { op:"mirror_multiply", inputs:["n_side"], out:"n_total" },
      { op:"overlap_correction", inputs:["SG:m1","axis"], out:"n_final" }
    ],
    invariants:["parity_preserved","mirror_equivalence"],
    answer_slot:"n_final"
  };
};

// 17.5 Symbolic Executor (Minimal)
export const executeMock = async (plan: Plan, sg: SceneGraph) => {
  const hasCross = sg.edges.some(e => e.rel === "cross");
  const n_side = hasCross ? 4 : 2; // demo rule
  const n_total = n_side * 2;      // mirror
  const n_final = n_total;         // no overlap for demo
  const trace: ProofTrace = { trace:[
    { step:1, rule:"symmetry_axis",    why:"fold line is axis" },
    { step:2, rule:"partition_count",   why:"cut partitions region" },
    { step:3, rule:"mirror_copy",       why:"symmetric duplication" },
    { step:4, rule:"overlap_check",     why:"no intersection double count" }
  ]};
  return { result:{ answer:n_final, slots:{ n_side, n_total, n_final } }, trace };
};

// 17.6 Verifier (Parity + Mirror)
export const verifyMock = async (result:any, sg:SceneGraph, plan:Plan) => {
  const parityOk = (result.answer % 2) === 0; // demo invariant
  const mirrorOk = true; // assume pass in mock
  const ok = parityOk && mirrorOk;
  const conf = ok ? 0.9 : 0.4;
  return { ok, conf };
};

// 17.7 Explainer (Dual)
export const explainMock = async (result:any) => ({
  child: "한쪽에서 나온 조각 수를 두 배 하면 돼요. 접은 선이 거울처럼 똑같이 만들거든요.",
  teacher: {
    principles: ["mirror_equivalence","overlap_correction"],
    justification:[
      "접힌 선은 대칭축 → 일대일 대응",
      "교차 절단이 없으므로 포함배제 보정 없음"
    ]
  }
});

// 17.8 Wire‑up
export const ReasonerMock: ReasonerAPI = {
  parseImage: parseImageMock,
  inferConcepts: inferConceptsMock,
  planStrategy: planStrategyMock,
  execute: executeMock,
  verify: verifyMock,
  explain: async (_r) => explainMock(_r)
};
```

---

## 18) Prompt Pack v0.2 — Few‑shot (2 유형)

**A. Symmetric‑Split (정답/오답 교정 포함)**

```
Input.text: "정사각형 종이를 한 번 접고 한 번 자르면 몇 조각?"
Input.SG: { axis:1, cuts:1, cross:false }
CSL_candidates: ["SYM","SPLIT"]
→ Output: TypeGuess=Symmetric-Split; Strategy=SYM-SPLIT/01; Final.answer=2×n_side …
오답패턴: 축 무시, 교차 중복 미보정 → anti_patterns 등록
```

**B. Lattice Path (장애물)**

```
Input.text: "오른쪽/아래로만 움직여 A→B 가는 경우의 수(× 장애물)?"
SG: grid 5×5, obstacle at (2,3)
→ Strategy=LATTICE/03; DP 테이블·경계조건·마스킹 출력 강제
```

---

## 19) Meta‑Controller v0.3 — Bandit Routing & Uncertainty

* **Bandit Router:** CSL 후보 전략들에 다중 무장강도기(Thompson/ε‑greedy) 적용 → 탐색/활용 균형.
* **Conformal Calibration:** 검증 패스 수·규칙 커버리지를 기반으로 conf 보정(예: Venn–Abers style).
* **Seeded Determinism:** `deterministic_seed` 슬롯 추가 → 재현성 확보, 결과 해시 포함.

AILO 확장 슬롯 예시:

```
route{obj:CG to:plan multi:2 policy:thompson seed:42}.
calibrate{obj:verdict to:conf rule:conformal k:5}.
```

---

## 20) Data Synthesizer v0.2 — 변형 생성기

* **대칭/분할 변형:** 축 수(1–3), 절단 수(1–4), 교차/비교차, 회전 추가
* **격자 경로:** 크기(4–8), 장애물 패턴(막대/점), 경계조건 스위프
* **타일링:** 단위 타일(2~3종), 배치 가능성/불가능성 라벨
* 출력: SG/CG/Plan/Final 일괄 생성, anti_patterns 자동 주입

---

## 21) Test Harness — A/B/C/D 자동 리포트

```bash
npx kangaroo-harness run \
  --dataset ./data/kangaroo-lower.jsonl \
  --modes baseline,csl,csl+se,full \
  --metrics acc,consistency,route_err,time \
  --seed 42 --trials 3 --out ./reports/v02.html
```

리포트: 정확도 곡선, 유형별 혼동행렬, 불변량 실패 히트맵, 오답설명 샘플.

---

## 22) v0.3 목표 요약

1. **Meta‑Controller**(bandit routing + conformal) 반영
2. **Lattice/03**·**Tiling/02** 실제 구현 + 반례 fuzzer 고도화
3. **Data Synthesizer**로 커리큘럼 Stage‑2~3 학습세트 생성
4. **Determinism 강화**: 해시 락 + seed 전파 + 시간 예산 가드
5. **Docset**: API 레퍼런스 자동 생성(SDK 타입 주석 기반)

— End of Evolution Patch (v0.2 → v0.3 준비) —

---

## 23) Demo Kit — Mini Dataset & Runner (v0.2)

> 바로 돌려볼 수 있는 **3문항 데모 세트(JSONL)**와 **간이 리포터** 추가.

### 23.1 `data/demo.v02.jsonl` (3 items)

```json
{"id":"D-01","text":"정사각형 종이를 한 번 접고 한 번 자르면 몇 조각?","SG":{"nodes":[{"id":"s1","kind":"shape","type":"square"},{"id":"l1","kind":"line","type":"fold"},{"id":"m1","kind":"mark","type":"cut"}],"edges":[{"src":"l1","dst":"s1","rel":"bisect"},{"src":"m1","dst":"s1","rel":"cross"}]},"CSL_candidates":["SYM","SPLIT"],"answer_type":"integer","bounds":[0,100],"gold":8}
{"id":"D-02","text":"오른쪽/아래로만 이동해 A에서 B까지 가는 경우의 수 (장애물 1개)","SG":{"grid":[5,5],"obstacles":[[2,3]]},"CSL_candidates":["LATTICE","CASE"],"answer_type":"integer","bounds":[0,1000],"gold":56}
{"id":"D-03","text":"빈칸에 알맞은 수를 넣으세요: 2, 5, 8, 11, (   )","SG":{},"CSL_candidates":["SEQUENCE","PATTERN"],"answer_type":"integer","bounds":[0,100],"gold":14}
```

### 23.2 `scripts/run-demo.ts`

```ts
import fs from "node:fs";
import readline from "node:readline";
import { ReasonerMock } from "../src/reasoner-mock"; // §17 구현체 경로 가정

async function* readJSONL(path: string) {
  const rl = readline.createInterface({ input: fs.createReadStream(path), crlfDelay: Infinity });
  for await (const line of rl) { if (line.trim()) yield JSON.parse(line); }
}

function acc(a:number,b:number){ return Math.round((a/b)*1000)/10; }

(async () => {
  const file = process.argv[2] ?? "./data/demo.v02.jsonl";
  let ok=0, total=0; const rows:any[] = [];

  for await (const item of readJSONL(file)) {
    total++;
    // 1) parse → 2) infer → 3) plan → 4) execute → 5) verify
    const sg = item.SG?.nodes ? item.SG : await ReasonerMock.parseImage(Buffer.alloc(0));
    const cg = await ReasonerMock.inferConcepts(sg);
    const plan = await ReasonerMock.planStrategy(sg, cg);
    const { result, trace } = await ReasonerMock.execute(plan, sg);
    const verdict = await ReasonerMock.verify(result, sg, plan);

    const pred = result.answer;
    const pass = typeof item.gold === "number" ? pred === item.gold : verdict.ok;
    if (pass) ok++;

    rows.push({ id:item.id, cls: cg.type_guess.class, strat: plan.strategy_id, pred, gold:item.gold, conf:verdict.conf, pass });
  }

  const accuracy = acc(ok,total);
  const report = {
    summary: { total, ok, accuracy_pct: accuracy },
    rows
  };

  fs.writeFileSync("./reports/demo.v02.json", JSON.stringify(report, null, 2));
  // Simple HTML
  const html = `<!doctype html><meta charset="utf-8"><title>Demo v0.2</title>
  <h1>Demo v0.2 — Report</h1>
  <p>Total: ${total}, OK: ${ok}, Accuracy: ${accuracy}%</p>
  <table border="1" cellpadding="6" cellspacing="0">
  <tr><th>ID</th><th>Type</th><th>Strategy</th><th>Pred</th><th>Gold</th><th>Conf</th><th>Pass</th></tr>
  ${rows.map(r=>`<tr><td>${r.id}</td><td>${r.cls}</td><td>${r.strat}</td><td>${r.pred}</td><td>${r.gold}</td><td>${r.conf.toFixed(2)}</td><td>${r.pass}</td></tr>`).join("")}
  </table>`;
  fs.writeFileSync("./reports/demo.v02.html", html);
  console.log("Wrote ./reports/demo.v02.{json,html}");
})();
```

### 23.3 `package.json` 스니펫

```json
{
  "scripts": {
    "demo": "tsx scripts/run-demo.ts",
    "report": "node scripts/run-demo.ts ./data/demo.v02.jsonl"
  },
  "devDependencies": { "tsx": "^4.19.0" }
}
```

---

## 24) LATTICE/03 & SEQ/02 — 규칙 표 채워넣기 안내

**LATTICE/03 핵심:**

* DP[i][j] = (i>0?DP[i-1][j]:0) + (j>0?DP[i][j-1]:0)
* 장애물(ox[i][j])이면 DP[i][j]=0
* 경계조건: DP[0][0]=1, 우상단/우하단 방향 정의 일치

**SEQ/02 핵심:**

* 차분 d = a[k]-a[k-1] 일정 시 n항 = a[1] + (n-1)d
* 주기/블록 탐색 실패 시 차분2, 3… 단계적 탐색, 과적합 방지용 반례 샘플 2개 강제 검증

---

## 25) Seeded Determinism — 실행 해시 규격

```
exec_seed: 42
hashes: {
  SG: "SG#d41d8cd...", Plan: "PL#9e107d9...", Result: "RS#e4d909c..."
}
policy: { time_budget_ms: 200, retries: 0 }
```

---

## 26) Quickstart (요약)

1. `npm i` 후 `npm run demo` (또는 `npm run report`) 실행.
2. `reports/demo.v02.html`에서 정밀도/오답 라인 확인.
3. §24 규칙 표 작성 후, D-02(격자), D-03(수열) 통과시키기.
4. 통과 후 **Sprint-2**로 TILING/02 추가 및 fuzzer 강화.

— Demo Kit Added (v0.2 runnable) —

---

## 27) Sprint‑2 Patch — v0.3 Core (TILING/02 · LATTICE/03 실제화 · Bandit Router · Conformal)

> 목표: **타일링/격자 규칙의 실제 계산**과 **메타 라우팅 안정화**. SDK 수준에서 재현 가능한 코드 골격 포함.

### 27.1 TILING/02 — 규칙·제약 명세

* **입력**: 단위 타일 집합 U = {u₁,…}, 보드 B(격자/폴리오미노), 회전/반전 허용여부, 빈칸/장애물.
* **필요조건**: 넓이 합치(∑area(u)·k = area(B)), 색칠 불변량(체커보드/삼색), 연결성.
* **충분조건(작은 보드)**: 백트래킹 + 대칭 가지치기 + 중복 회피(폴리오미노 정규형).
* **출력**: 배치 가능 여부/경우의 수, 불가 사유(불변량 실패 항목).

### 27.2 LATTICE/03 — 구현 체크리스트

* DP 테이블 생성, 장애물 마스킹, 경계조건.
* 특별칸(가중) 옵션: DP[i][j] *= w[i][j] (정수 가중), overflow 가드는 mod 10⁹+7 선택가능.

### 27.3 Bandit Router (Thompson Sampling)

* 팔(arms): 상위 CSL 후보×전략 템플릿 조합.
* 보상: 검증 통과(1)·실패(0), + 소폭 가산(conf>τ).
* 업데이트: Beta(α,β) 사후 갱신 → 샘플 상 argmax 선택.

### 27.4 Conformal Calibration (Venn–Abers 스타일)

* 특성: rule_coverage, tests_passed, time_budget_margin.
* 보정: Platt/Isotonic 중 택1, 작은 셋에서 교차검증.

---

## 28) 코드 골격 — Router · Calibration · Tiling/Lattice (TS)

```ts
// 28.1 Bandit Router
export class BanditRouter {
  private arms: string[]; // e.g., ["SYM-SPLIT/01","LATTICE/03",...]
  private alpha: Record<string,number> = {}; // success
  private beta:  Record<string,number> = {}; // failure
  constructor(arms:string[]) { this.arms = arms; arms.forEach(a=>{this.alpha[a]=1; this.beta[a]=1;}); }
  sampleBeta(a:string){ const u=Math.random(), v=Math.random(); const α=this.alpha[a], β=this.beta[a];
    // Approx Beta via inverse‑CDF (simple): use log trick
    return Math.pow(u, 1/α) / ( Math.pow(u, 1/α) + Math.pow(v, 1/β) );
  }
  select(){ return this.arms.map(a=>({a,s:this.sampleBeta(a)})).sort((x,y)=>y.s-x.s)[0].a; }
  update(a:string, reward:number){ if(reward>0) this.alpha[a]+=1; else this.beta[a]+=1; }
}

// 28.2 Conformal (isotonic stub)
export function conformalCalibrate(raw:number, feats:{coverage:number; tests:number; margin:number}){
  const z = 0.5*raw + 0.3*feats.coverage + 0.2*Math.tanh(feats.tests + feats.margin*0.1);
  return Math.max(0, Math.min(1, z));
}

// 28.3 LATTICE/03
export function latticePaths(w:number,h:number, obstacles:Set<string>){
  const key=(i:number,j:number)=>`${i},${j}`; const DP = Array.from({length:w},()=>Array(h).fill(0));
  for(let i=0;i<w;i++) for(let j=0;j<h;j++){
    if(obstacles.has(key(i,j))){ DP[i][j]=0; continue; }
    if(i===0 && j===0){ DP[i][j]=1; continue; }
    DP[i][j] = (i>0?DP[i-1][j]:0) + (j>0?DP[i][j-1]:0);
  }
  return DP[w-1][h-1];
}

// 28.4 TILING/02 — checkerboard invariant + small backtrack
export function tilingFeasible(board:boolean[][], tiles:number[][][]){
  // checkerboard invariant
  const H=board.length, W=board[0].length; let diff=0;
  for(let i=0;i<H;i++) for(let j=0;j<W;j++) if(board[i][j]) diff += ((i+j)%2?1:-1);
  const tileDiff = tiles.reduce((s,t)=> s + t.reduce((ss,[x,y])=> ss + ((x+y)%2?1:-1), 0), 0);
  if(Math.abs(diff)%Math.abs(tileDiff||1)!==0) return {ok:false, reason:"checkerboard"};
  // small‑board backtracking (demo):
  const used:Array<[number,number]> = [];
  function place(idx:number):boolean{
    // find first empty
    let x=-1,y=-1; outer: for(let i=0;i<H;i++) for(let j=0;j<W;j++) if(board[i][j]){ x=i; y=j; break outer; }
    if(x<0) return true; // filled
    for(const shape of tiles){
      const cells = shape.map(([dx,dy])=>[x+dx,y+dy] as [number,number]);
      if(cells.every(([i,j])=> i>=0&&i<H&&j>=0&&j<W && board[i][j])){
        // place
        cells.forEach(([i,j])=> board[i][j]=false); used.push([x,y]);
        if(place(idx+1)) return true;
        // backtrack
        cells.forEach(([i,j])=> board[i][j]=true); used.pop();
      }
    }
    return false;
  }
  const ok = place(0);
  return { ok, reason: ok?"":"no‑packing" };
}
```

---

## 29) Data Synthesizer v0.3 — 생성 규칙

* **Tiling**: 보드크기 4–8, 타일 집합 {도미노, L‑트리오미노}, 회전/반전 옵션 스위프.
* **Lattice**: 격자 4–8, 장애물 패턴(막대/코너/중앙), gold는 DP로 생성.
* **Sequence**: 등차/등비/블록혼합(교란 1~2개) + 반례 샘플 자동 첨부.
* 산출: `(SG, CG_guess, Plan_guess, gold, anti_patterns)` 일괄.

---

## 30) Harness 업그레이드 — 유형별 리더보드 & 혼동행렬

* 리포트에 `type_acc`, `conf_hist`, `route_err_by_type`, `anti_pattern_hits` 추가.
* HTML에 heatmap 삽입(간단 캔버스 렌더).

---

## 31) Roadmap v0.3 → v0.6 → 1.0

* **v0.3 (지금)**: TILING/02·LATTICE/03 실제화, Router+Conformal, Synthesizer v0.3.
* **v0.4**: VP 업그레이드(도형/텍스트 합성 추론), SE 기하(넓이/둘레) 확장, 반례 fuzzer 2.0.
* **v0.5**: Curriculum Stage‑4~5(검증 사고·듀얼 설명) 미세조정, 저학년 실데이터 400+ A/B.
* **v0.6**: Determinism 강화(전 단계 해시·시간 가드), SDK Beta, 통합 리포트.
* **1.0 LTS**: 사양 고정, 템플릿 10+, 합의형 메타‑라우팅, 공개 데이터셋·리더보드.

---

## 32) 실행 지침 (즉시 적용)

1. §28 LATTICE/03 함수를 러너에서 호출하도록 연결하고, D‑02 정답 매칭.
2. §28 TILING/02의 `tilingFeasible`로 작은 보드 문제 통과 확인.
3. BanditRouter를 Strategy Planner에 삽입, 보상은 `verdict.ok`로 갱신.
4. `conformalCalibrate`를 검증 conf 산출 후 최종 conf로 보정하여 리포트에 기록.

---

## 33) 안전·품질 가드 (v0.3)

* **근거 참조 강제**: ProofTrace 미참조 설명 차단.
* **재현성**: seed 전파 + 해시 잠금 + 시간 예산 고정.
* **데이터 윤리**: 공개/합성만 사용, 개인 식별 없음.
* **행동형 조언 금지**: 교육/연구 목적 한정.

— v0.3 Patch Applied —

---

## 34) Sprint‑3 Patch — v0.4 Core (VP 업그레이드 · 기하 넓이/둘레 · Fuzzer 2.0 · 리포트 강화)

> 목표: **시각 전처리 신뢰도↑**, **초등 기하 계산 커버리지↑**, **반례 생성기 고도화**, **오류 가시화**.

### 34.1 Visual Parser v0.4 — Tokenizer & Robust SG

* **Primitive tokens**: `point(lineEnd/corner)`, `segment(line/fold/cut)`, `arc`, `text`, `bbox`.
* **Grouping**: 연접·평행·교차·동일 길이 후보 → `shape`(polygon/rect/triangle/circle) 합성.
* **Axis detection**: 대칭 후보 축 스코어링(평행 집합·양측 대응점 분포·중앙선).
* **OCR slot**: `ocr_tokens:[{text, bbox, conf}]` (Tesseract 등 외부 교체 가능) – 목업은 고정 토큰 반환.
* **Noise guard**: 길이·각도 quantization(격자 스냅), 너무 짧은 segment 제거.

SG 예시(추가 필드):

```json
{
  "nodes": [
    {"id":"p1","kind":"point","pos":[10,10]},
    {"id":"seg1","kind":"segment","type":"fold","p1":"p1","p2":"p2","len":100},
    {"id":"poly1","kind":"shape","type":"polygon","verts":["p1","p2","p3","p4"]}
  ],
  "attrs": { "grid_snap": 1.0, "ocr_tokens": [{"text":"?","bbox":[..],"conf":0.93}] }
}
```

---

### 34.2 SE Geometry v0.4 — Area/Perimeter Primitives

```ts
// Shoelace area for lattice polygons (unit^2)
export function polygonAreaLattice(pts: Array<[number,number]>) {
  let s=0; for(let i=0;i<pts.length;i++){ const [x1,y1]=pts[i], [x2,y2]=pts[(i+1)%pts.length]; s += x1*y2 - x2*y1; }
  return Math.abs(s)/2;
}

// Perimeter on grid (Manhattan edges or Euclid)
export function polygonPerimeterGrid(pts: Array<[number,number]>, metric:"L1"|"L2"="L1"){
  let p=0; for(let i=0;i<pts.length;i++){ const [x1,y1]=pts[i], [x2,y2]=pts[(i+1)%pts.length];
    const dx=Math.abs(x1-x2), dy=Math.abs(y1-y2);
    p += metric==="L1"? dx+dy : Math.hypot(dx,dy);
  } return p;
}

// Decompose rect/triangles within snapped grid
export function areaByDecomposition(shapes:{type:"rect"|"tri", dims:number[]}[]) {
  return shapes.reduce((a,s)=> a + (s.type==="rect"? s.dims[0]*s.dims[1] : (s.dims[0]*s.dims[1])/2 ), 0);
}

// Unit counting with symmetry copy
export function symmetricCount(nSide:number, factor:number=2, overlap:number=0){ return nSide*factor - overlap; }
```

* **적용 유형**: 격자 도형 넓이, 둘레, 분할 후 합성, 대칭 복제.
* **검증**: Pick's Theorem quick‑check(격자 폴리곤) – `A = I + B/2 − 1` (I=내점, B=경계점) 비교.

---

### 34.3 Fuzzer 2.0 — 반례·교란 시나리오

* **SG Perturb**: 미세 회전(±1~2°), 길이 ±1칸, segment 누락/중복, 텍스트 OCR 오탈자.
* **Rule Edge‑cases**: 대칭축 오프셋, 교차 절단 중첩, 격자 경계 접촉.
* **Oracle**: 작은 케이스는 완전탐색/브루트, 기하는 Shoelace/Pick로 이중 계산 비교.
* **Labeler**: 실패 시 `anti_patterns` 자동 주입(예: "축 무시", "중복 보정 누락").

---

### 34.4 Report v0.4 — 오류 시각화

* **SVG Overlay**: SG를 SVG로 렌더, 오답 단계의 노드/엣지 하이라이트.
* **Heatmaps**: 라우팅 오류 히트맵, conf 분포, 불변량 실패 밀도.
* **Trace Viewer**: ProofTrace step별 규칙 ID와 입력/출력을 표로 병렬 표시.

---

## 35) Prompt Pack v0.4 — Geometry & OCR Few‑shots

* **Area (Shoelace)**: 다각형 좌표/격자점 제공 → step: 좌표 정렬 → Shoelace → Pick cross‑check.
* **Perimeter (Grid)**: L1 경계만 허용되는지 명시 → 잘못된 L2 사용 금지 예시 포함.
* **OCR 교정**: 숫자/기호 `0/O`, `1/l` 구분 규칙 → conf<0.6이면 인간 검토 슬롯.

입출력 슬롯에 `geo_check:{picks:pass|fail, shoelace:val}` 추가.

---

## 36) Curriculum Stage‑4/5 (Verification & Dual Explain) 업그레이드

* **Stage‑4**: 반례 생성 → 규칙 보정 → 재검증 루프 2회 이상 필수.
* **Stage‑5**: 아동용/교사용 설명 상호 일관성 체크리스트(용어·근거·단계 매칭).

---

## 37) Harness v0.4 — 시각 리포트 통합

```bash
npx kangaroo-harness run \
  --dataset ./data/kangaroo-lower.v04.jsonl \
  --modes baseline,csl,csl+se,full \
  --viz svg,heatmap,trace \
  --seed 123 --trials 5 --out ./reports/v04.html
```

---

## 38) Roadmap Update (→ v0.6)

* **v0.5**: VP 노이즈 억제(허프+RANSAC 목업), 텍스트 조건 파서, 기하 혼합문항.
* **v0.6**: Determinism 전파(해시 체인), SDK Beta 발행, 공개 미니 리더보드 스펙.

— v0.4 Patch Applied —

---

## 39) Sprint‑4 Patch — v0.5 Core (VP 노이즈 억제 · 텍스트 조건 파서 · 혼합문항)

> 목표: **시각 노이즈에 강건**, **문장 조건을 구조화**, **혼합형 문항 라우팅**. 1.0 전 마지막 대규모 안정화.

### 39.1 VP v0.5 — Hough/RANSAC 목업 내장

* **Hough(line) stub**: 격자 스냅 후 누적공간에서 주요 직선 후보 k개.
* **RANSAC**: 선/원 후보 적합 → 외란점(outlier) 제거 → `segment/arc` 재구성.
* **Merge & Snap**: 유사 각·길이 segment 병합, 정규화된 각도(0/45/90/135°) 근사.

```ts
export function houghLinesMock(points:[number,number][], k=4){ /* return k major lines */ }
export function ransacFitLine(points:[number,number][], iters=200, tol=1.0){ /* inliers/outliers */ }
export function ransacFitCircle(points:[number,number][], iters=200, tol=1.5){ /* cx,cy,r */ }
```

SG 확장 필드: `noise:{snr:number, dropped_segments:number, snapped:boolean}`

---

### 39.2 Text Condition Parser v0.5 — 수학적 제약 추출

* 정규식+규칙: 수량/단위/비교(최대·최소), 이동 제약(오른쪽/아래), 반복 횟수(“두 번 접고”) 등.
* 출력 슬롯 예시:

```json
{
  "constraints": {
    "moves": ["RIGHT","DOWN"],
    "folds": 2,
    "answer_type": "integer",
    "bounds": [0, 1000]
  }
}
```

* **오류 방지**: 모호 표현(“대략”, “비슷하게”) 플래그 → 인간 검토 슬롯.

---

### 39.3 Mixed‑Type Router — CSL×Text×SG 합의

* 입력: `CSL_candidates` + `text_constraints` + `SG.attrs`.
* 규칙: 2/3 합의 시 채택, 미합의는 `re-map` 후 bandit prior 반영.
* 예: `LATTICE` 후보이나 텍스트에 “대각선 금지”가 있으면 `L1` 경로 강제.

---

### 39.4 SE 확장 — 혼합 연산 파이프

* `geo → comb → parity` 순/또는 `comb → geo` 순서 선택(플래너가 결정).
* 예: 타일링 가능성 판정(불변량) → 가능 시 경우의 수(조합) 산출.

---

### 39.5 Error Taxonomy v0.5

* **E5 텍스트-도식 충돌**: 문장 조건과 CSL 전략 충돌 시 라우팅 실패로 기록.
* **E6 과적합 규칙**: 특정 템플릿에서만 맞고 일반화 실패 → anti_patterns 강화.

---

### 39.6 Synthesizer v0.5

* **텍스트 변이**: 동치 표현(“오른쪽/아래” ↔ “왼쪽/위 금지”), 수사적 표현 삽입.
* **노이즈 주입**: 점/선 누락·추가, 경계 살짝 벗어남, OCR 혼동(0/O, 1/l) 비율 조절.

---

### 39.7 Harness v0.5 — 합의·충돌 리포트

* `agreement_rate(CSL,Text,SG)`, `conf_delta(before/after conformal)`, `E5/E6` 카운트.
* SVG 위에 텍스트 제약 배지 렌더.

---

### 39.8 SDK 업데이트 (β 준비)

```ts
export interface ReasonerAPIv05 extends ReasonerAPI {
  parseText(text:string): Promise<{constraints:any, flags:{ambiguous:boolean}}>
  routeMixed(sg:SceneGraph, cg:ConceptGraph, tc:any): Promise<Plan>
}
```

---

### 39.9 Quick Checks → v0.6 진입 조건

1. 데모+합성 200문항에서 `agreement_rate ≥ 0.8`.
2. `E5/E6 ≤ 10%`.
3. 밴딧/컨포멀 활성화 상태에서 정확도 **+3pp↑**, 일관성 **+10%↑**.

---

## 40) Roadmap v0.6 (SDK Beta · 해시 체인 · 미니 리더보드)

* **Determinism Chain**: SG→CG→Plan→Result→Verdict의 해시 연쇄와 seed 전파.
* **SDK Beta 배포 규격**: 타입 정의·예외·시간가드·로깅 인터페이스.
* **Mini Leaderboard**: 유형별 정확도·일관성·conf@τ, 오답 예시 묶음.

— v0.5 Patch Applied —

---

## 41) Sprint‑5 Patch — v0.6 Core (Determinism Chain · SDK Beta · Mini Leaderboard · Release Gate)

> 목표: **재현성 절대 보장**, **SDK Beta 규격 완성**, **공개 미니 리더보드**, **1.0 진입 게이트** 마련.

### 41.1 Determinism Chain — Hash & Seed Propagation

* 각 단계 산출물과 설정을 해시로 체인 연결.
* 해시 입력: 직렬화된 정규 JSON + 버전 + seed + 정책.
* 위변조 방지: 후단 단계는 선행 해시를 반드시 포함.

```ts
export type Hash = `SG#${string}` | `CG#${string}` | `PL#${string}` | `RS#${string}` | `VD#${string}`;
export interface Determinism {
  seed:number; // default 42
  chain:{ SG:Hash; CG:Hash; Plan:Hash; Result:Hash; Verdict:Hash };
}

export function hashOf(tag:string, obj:any): Hash {
  const json = JSON.stringify(obj);
  const h = crypto.subtle ? "todo" : require("node:crypto").createHash("sha256").update(json).digest("hex");
  return `${tag}#${h.slice(0,16)}` as Hash;
}
```

**정책:** `time_budget_ms`, `retries`, `router_policy`, `conformal_on` 등도 해시에 포함.

---

### 41.2 SDK Beta (v0.6) — Interfaces & Errors

```ts
export enum ErrCode {
  ROUTE_MISALIGN = "E5",   // 텍스트-도식 충돌
  OVERFIT_TEMPLATE = "E6",  // 과적합 규칙 탐지
  TIME_BUDGET = "E7",
  HASH_MISMATCH = "E8",
  INSUFF_EVIDENCE = "E9"     // ProofTrace 근거 부족
}

export interface Logger {
  info(msg:string, meta?:any):void; warn(msg:string, meta?:any):void; error(msg:string, meta?:any):void;
}

export interface RunPolicy { time_budget_ms:number; retries:number; seed:number; router:"thompson"|"eps"; conformal:boolean; }

export interface ReasonerAPIv06 extends ReasonerAPIv05 {
  run(problem:{text:string, image?:Buffer, SG?:SceneGraph}, policy:RunPolicy, log?:Logger): Promise<{
    answer:any, conf:number, chain:Determinism["chain"], errors:ErrCode[], report:any
  }>;
}
```

**로깅 표준:** `event@stage` 키(`parse@vp`, `route@csl`, `prove@se`, `check@vf`, `explain@ex`)와 ISO 시간.

---

### 41.3 Mini Leaderboard — Spec & Metrics

* **입력**: JSONL (id, text, SG|image, gold, type_tag)
* **메트릭**: `acc`, `consistency`(retry 3), `route_err`, `conf@τ` (τ∈{0.7,0.8,0.9}), `time@p50/p90`.
* **유형 리더보드**: SYM/SPLIT/LATTICE/TILING/SEQ/COMPARE별 분할.

```json
{"id":"K21-P1","type":"SYM","gold":8,"conf":0.91,"pred":8,"ok":true,"time_ms":57}
```

**리포트요구:** random‑seed 목록, 해시 체인 요약, 실패 Top‑N 트레이스 링크.

---

### 41.4 Release Gate — 1.0 LTS 진입 조건

1. **정확도**: 저학년 이미지형 샘플셋(≥600)에서 Baseline(CoT) 대비 **+15pp 이상**.
2. **일관성**: 재시도 동일률 **≥ +30%p**.
3. **라우팅 오류율**: `route_err ≤ 7%` (v0.5 목표 유지 또는 개선).
4. **근거충실**: ProofTrace 규칙 커버리지 **≥ 90%**.
5. **결정론**: seed 동일 시 해시 체인 동일률 **100%**.
6. **안전/윤리**: 개인정보 0, 저작권 준수, 행동형 조언 금지.

---

### 41.5 CLI — One‑Shot Runner & Leaderboard

```bash
# 단일 문제 실행
kangaroo run \
  --text "정사각형 종이를 한 번 접고 한 번 자르면 몇 조각?" \
  --seed 42 --time 200 --router thompson --conformal on

# 데이터셋 평가 + 리더보드 생성
kangaroo eval \
  --data ./data/kangaroo-lower.v06.jsonl \
  --out ./reports/v06.html --trials 3 --seeds 41,42,43
```

---

### 41.6 Public Package Layout (Proposed)

```
packages/
  reasoner-sdk/           # SDK (TS) — types, runner, router, conformal
  reasoner-core/          # VP/CSL/SE/VF core (mock + replaceable hooks)
  reasoner-cli/           # CLI (esbuild)
  reasoner-report/        # leaderboard generator (html/svg)
  datasets/               # jsonl samples + schema validators
```

---

### 41.7 Migration Notes (v0.4/0.5 → v0.6)

* `ReasonerAPIv05.routeMixed` → 통합 `run()` 내부에서 호출되도록 변경.
* conf는 항상 **conformal 보정 후 값**을 표준 출력으로.
* 리포트는 해시 체인 요약을 상단 배치.

---

### 41.8 v0.6 Quick Checklist

* [ ] 해시 체인 전 단계 적용(테스트 포함)
* [ ] Logger 주입으로 이벤트 타임라인 생성
* [ ] Mini Leaderboard로 v0.4/0.5 대비 게인 검증
* [ ] Release Gate 6항목 중 4항목 선충족 → v0.7에서 잔여 달성

— v0.6 Patch Applied —

---

## 42) Sprint‑6 Patch — v0.7 (Docs · Packaging · Tests · Policy · RC 준비)

> 목표: **실사용 배포 준비**. 문서 자동생성, 패키지 레이아웃 확정, 테스트 매트릭스, 윤리/데이터 가이드, 릴리즈 관리를 정리해 **RC(Release Candidate)** 상태로 끌어올림.

### 42.1 Docs Pipeline — Auto‑Docs & Spec Sync

* **Typedoc**로 SDK/코어 주석 → API 문서 자동생성.
* **Spec Sync**: §1~§41의 스키마/프로토콜을 `spec/` 폴더로 추출, JSON Schema(+Zod) 동시 관리.
* **How‑To** 문서 템플릿(아래 §42.7) + 예제(SYM/LATTICE/TILING/SEQ).

```bash
npm run docs   # typedoc → docs/api/
npm run spec   # zod → json‑schema 동기화
```

---

### 42.2 Packaging — Monorepo 레이아웃 확정

```
packages/
  core/                # VP/CSL/SE/VF + router + conformal (lib)
  sdk/                 # ReasonerAPI v0.6+ wrapper, run(), logger
  cli/                 # kangaroo {run,eval}
  report/              # html/svg leaderboard
  schemas/             # zod + json‑schema, validators
  examples/            # demo datasets + scripts
```

* **Build**: esbuild(ts) → ESM+CJS 듀얼 타겟, tree‑shaking 허용.
* **Versioning**: semver, `0.7.x`는 RC 라인, `1.0.0` LTS에서 API 고정.

---

### 42.3 Test Matrix — Determinism & Robustness

* **Determinism**: 동일 seed에서 SG→…→Verdict 해시 체인 100% 일치.
* **Robustness**: Fuzzer 2.0 변이(각 20샷) 이후 정답/불변량 유지율.
* **Router A/B**: thompson vs ε‑greedy 정확도/시간/route_err 비교.
* **Conf Calibration**: conformal on/off에서 `ECE`(Expected Calibration Error) 리포트.

```bash
npm run test:det   # 해시 체인
npm run test:fuzz  # 변이 강건성
npm run test:router
npm run test:cal
```

---

### 42.4 Policy Pack — Ethics · Data · Safety

* **Ethics**: 교육/연구 목적, 아동 대상 설명의 정확성·친화성 가이드.
* **Safety**: ProofTrace 근거 미충족 시 출력 차단(Err E9), conf<τ시 “모름” 채택.
* **Data**: 공개/합성 데이터만 사용, 라이선스 명시. 민감정보 0 원칙.
* **Responsible Disclosure**: 오류/편향 리포트 채널과 SLA.

---

### 42.5 Security & Privacy

* **No PII**: 입력/출력/로그에서 PII 필드 금지.
* **Hash‑only Trace**: 외부 공유 파일에는 해시 요약만 포함, 원데이터 비공개 옵션.
* **Supply Chain**: 서드파티 라이브러리 SBOM 생성(`npm run sbom`).

---

### 42.6 Performance Budget

* 1문항 평균 **≤ 300ms**(Mock 기준), p90 **≤ 800ms**.
* 시간 초과 시 Err E7 + 대체 경로(더 단순한 전략) 자동 폴백.

---

### 42.7 README Skeleton (EN/KR)

````md
# AILO–Kangaroo Reasoner (RC)

**Goal**: Reliable reasoning for early‑grade, image‑heavy math (Kangaroo/MathArena‑like).

## Quickstart
```bash
npm i @ailo/reasoner-cli -g
kangaroo run --text "Fold a square once and cut once; how many pieces?" --seed 42
````

## Why it works

* Visual → Schema → Symbolic tri‑layer
* Bandit routing + Conformal calibration
* Determinism chain for reproducibility

## Packages

core · sdk · cli · report · schemas · examples

## Safety & Data

* Proof‑based explanations; no hallucinated steps
* Public/synthetic datasets only

---

# AILO–Kangaroo Reasoner (한국어)

## 빠른 시작

```bash
npm i @ailo/reasoner-cli -g
kangaroo run --text "정사각형 종이를 한 번 접고 한 번 자르면 몇 조각?" --seed 42
```

## 작동 원리

지각(시각) → 도식(CSL) → 기호(SE) 3계층 + 밴딧 라우팅 + 컨포멀 보정 + 해시 체인

```

---

### 42.8 Release Notes Template
```

## v0.7.0‑rc1 (YYYY‑MM‑DD)

* Added: determinism chain, docs pipeline, test matrix
* Changed: SDK run() unified, conformal default=on
* Fixed: lattice boundary off‑by‑one in DP init
* Security: SBOM generation & dependency audit

````

---

### 42.9 RC Gate — 체크리스트
- [ ] Docs/API/Spec 동기화 100%
- [ ] Test Matrix 통과
- [ ] Mini Leaderboard 공개(데이터셋·지표 명시)
- [ ] License/NOTICE 포함(MIT)
- [ ] CLI/SDK 예제 실행 성공

---

### 42.10 1.0 LTS Plan (Preview)
- API 고정(ReasonerAPI v1.0), 템플릿 ≥ 10, 공개 벤치/리더보드.
- Determinism 강화(옵션 해시 솔트, 체인 서명), 문항 커버리지 확대.
- 문서: 튜토리얼(10문항), 트러블슈팅, 확장 가이드(새 템플릿 추가법).

— v0.7 Patch Applied (RC‑Ready) —



---

## 43) 1.0 LTS Patch — Finalized Spec (API Freeze · Template 10+ · Compliance · Release)
> 목표: **언어/프로토콜/SDK API 고정**, 템플릿 10+ 완비, 준수규정·리더보드 포맷 확정. 장기 지원(LTS) 기준 수립.

### 43.1 ReasonerAPI v1.0 — Frozen Interfaces
```ts
export type Seed = number;
export type HashTag = `SG#${string}`|`CG#${string}`|`PL#${string}`|`RS#${string}`|`VD#${string}`;

export interface DeterminismChain { seed: Seed; SG:HashTag; CG:HashTag; Plan:HashTag; Result:HashTag; Verdict:HashTag }
export interface RunPolicyV1 { time_ms:number; retries:0|1; router:"thompson"|"eps"|"none"; conformal:boolean; metric:"L1"|"L2"; }
export interface EvidenceRef { rule_id:string; inputs:any; outputs:any }

export interface RunInput {
  id?: string;
  text: string;
  image?: Buffer;
  SG?: SceneGraph; // optional pre‑parsed
  constraints?: any; // optional parsed text constraints
}

export interface RunOutput {
  answer: any;
  conf: number;            // conformal‑calibrated if enabled
  chain: DeterminismChain; // hash chain
  type: string;            // final routed class
  strategy: string;        // template id
  proof: ProofTrace;       // must cover ≥1 rule/step
  checks: string[];        // invariants that passed
  errors: ErrCode[];       // if any
  report?: any;            // impl‑specific
}

export interface ReasonerV1 {
  run(input:RunInput, policy?:RunPolicyV1): Promise<RunOutput>;
}
````

* **불변 규칙**: 필드명·타입·의미 고정. 하위호환 이슈는 minor/patch로만 수정.

---

### 43.2 Template Catalog v1.0 — 12 Templates

* **SYM‑SPLIT/01** (대칭 분할 기본)
* **SYM‑ROT/02** (회전 대칭 복제)
* **TILING/02** (도미노/L‑트리오미노 타일링 가능성)
* **TILING‑COUNT/03** (작은 보드 경우의 수)
* **LATTICE/03** (격자 경로 기본 + 장애물)
* **LATTICE‑WEIGHT/04** (가중 칸 경로 합)
* **COMP/01** (보수 합/자리수 규칙)
* **SEQ/02** (등차/등비/블록)
* **PATTERN/01** (주기/차분 혼합 규칙 귀납)
* **COMPARE/01** (최소/최대/비교 불변량)
* **AREA/01** (Shoelace+Pick 교차검증)
* **PERIM/01** (격자 둘레 L1/L2 구분)

각 템플릿은 `rule_id`, `preconds`, `steps`, `invariants`, `anti_patterns`, `complexity_hint` 포함.

---

### 43.3 Compliance & Safety v1.0 — Hard Gates

* **E9(INSUFF_EVIDENCE)**: ProofTrace 미충족 시 **출력 불가**. `answer` null, `errors:[E9]`, `conf=0`.
* **Conf Floor**: `conf<0.5`이면 `answer` 대신 `ASK‑FOR‑CLARITY` 응답(인간검토 슬롯).
* **Time Budget**: `time_ms` 초과 시 E7 + 폴백 템플릿 1회만 허용.
* **Determinism**: 동일 seed/입력에서 해시 체인 동일률 100% 아닌 경우 E8.

---

### 43.4 Dataset Schema v1.0 — JSONL

```json
{"id":"K21-P1","type":"SYM","text":"…","image":"path|data","SG":{…},"gold":8,"tags":["grade1","symmetry"],"source":"public|synthetic","license":"…"}
```

* **필수**: id, type, text, gold. 이미지 또는 SG 중 하나는 필수.
* **권장**: source, license, tags(난이도/유형), rationale(정답 근거 요약).

---

### 43.5 Leaderboard v1.0 — Fields & Ranks

* 전역 메트릭: `acc`, `consistency`, `route_err`, `ECE`, `time@p50/p90`.
* 타입별 슬라이스: 각 유형 템플릿별 `acc@type`.
* **랭크 규칙**: acc 동률 시 consistency → route_err 낮은 순 → ECE 낮은 순.
* **공개 항목 제한**: 학생 보호 위해 오답 원문항 직접 이미지 링크는 제외(요약/해시만).

---

### 43.6 Release Bundle v1.0 — 구조

```
release/
  spec/                 # canonical schemas (json, zod)
  sdk/                  # @ailo/reasoner‑sdk v1.0.0
  cli/                  # kangaroo v1.0.0
  report/               # leaderboard generator
  datasets/             # sample (100 공개/합성)
  docs/                 # html (typedoc + guides)
  LICENSE, NOTICE, SECURITY.md, ETHICS.md
```

---

### 43.7 Migration Guide (0.6/RC → 1.0)

* `ReasonerAPIv06.run(policy.RunPolicy)` → `ReasonerV1.run(policy:RunPolicyV1)`로 교체.
* `metric` 기본값: L1. (문항에서 L2 요구 시 policy로 지정)
* `conf`는 항상 보정치. 원시값이 필요하면 `report.raw_conf` 제공(옵션).
* `errors`는 문자열 코드 유지(E5…E9). 신규 코드는 1.x minor에서만 추가.

---

### 43.8 FAQs (운영)

* **Q: 이미지 없이도 되나요?** A: SG가 제공되면 이미지 생략 가능. 반대로도 가능.
* **Q: 답이 여러 개인 문항?** A: `gold`를 집합·범위로 표현. Verifier가 허용판정.
* **Q: 속도 튜닝?** A: time_ms를 낮추면 라우터 탐색 팔 수를 제한.
* **Q: 신뢰도 임계?** A: 교육 현장 권장 `τ=0.7`.

---

### 43.9 Examples (KR/EN)

* **KR**: "정사각형 종이를 두 번 접고 한 번 자를 때 조각 수" → SYM‑ROT/02 + SYM‑SPLIT/01 합성.
* **EN**: "How many shortest paths from A to B when a 2×1 block obstacle is placed at (2,2)?" → LATTICE/03.

---

### 43.10 1.0 LTS Gate — 최종 체크

* [ ] Template 12 종 모두 테스트 통과(정확도·근거·시간)
* [ ] Dataset 600+에서 Release Gate(§41.4) 만족
* [ ] Leaderboard v1.0 공개(요약/해시), SBOM 첨부
* [ ] README(EN/KR)·Docs·Spec 일치 확인(자동 검사 통과)
* [ ] 버전 태그 `v1.0.0` + 변경사항 로그 기록

— **1.0 LTS Spec Applied** —
