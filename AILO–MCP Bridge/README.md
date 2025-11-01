# 🌐 AILO–MCP Bridge v1.0 LTS

**Self-Contained Standard Edition** · MIT License

---

## 🧭 Overview (English)

**AILO–MCP Bridge v1.0 LTS** is a long-term stable release of the AILO ecosystem.
It unifies the **AILO Intent Language**, **Bridge Kernel**, and **Model Context Protocol (MCP)** into a self-contained runtime and SDK.

> **Goal:** Let AI systems reason, act, and interact deterministically and safely.

---

### 🔑 Key Features

* **Deterministic Execution** — same input + policy → same result
* **Traceable Decisions** — every action is hashed and auditable
* **Policy-as-Code** — risk/rule/conf govern all actions
* **Unified Bridge Layer** — standard MCP for tools, APIs, memory
* **SDK / CLI / API Ready**

---

### ⚙️ Runtime Flow

```
User Intent → AILO Grammar → Bridge Kernel → MCP Layer → Result + Trace
```

---

## 🚀 Quick Start

### NodeJS

```bash
npm i @ailo-mcp/bridge
```

```ts
import { Bridge, loadPolicy } from "@ailo-mcp/bridge";

const policy = await loadPolicy("./policies/v1/tenant-kr");
const bridge = new Bridge({ policy });

const plan = {
  intent: { verb: "summarize", obj: "KOSPI outlook", conf: 0.9, risk: "low" }
};

const out = await bridge.run(plan);
console.log(out.result, out.meta.policy_hash, out.trace_id);
```

### Python

```bash
pip install ailo-mcp-bridge
```

```python
from ailo_mcp import Bridge, load_policy

policy = load_policy("./policies/v1/tenant-kr")
b = Bridge(policy=policy)
plan = {"intent":{"verb":"summarize","obj":"KOSPI outlook","conf":0.9,"risk":"low"}}
result = b.run(plan)
print(result["result"], result["meta"]["policy_hash"], result["trace_id"])
```

---

## 🧩 Example Prompts

| Task            | Natural Prompt                                     | Internal AILO Form                                                          |
| --------------- | -------------------------------------------------- | --------------------------------------------------------------------------- |
| **Summary**     | “Summarize today’s KOSPI market news.”             | `summarize{obj:"KOSPI news",rule:["tone:analytical"],conf:0.9}!`            |
| **Translation** | “Translate this paragraph to Korean, poetic tone.” | `translate{obj:"<text>",to:"ko",style:{tone:"lyric"},conf:0.9}!`            |
| **Analysis**    | “Compare Apple and Samsung’s quarterly profits.”   | `compare{obj:"Apple vs Samsung profits",rule:["metric:profit"],conf:0.92}!` |
| **Reflection**  | “Review the last output for tone drift.”           | `reflect{obj:"last output",rule:["tone-check"],conf:0.95}.`                 |

---

### 📘 Default Policies

* Scope control (`read:web`, `write:memory`)
* PII masking (email, phone)
* Rate and budget limits
* Trace ID + policy hash per result

---

### 📄 License

MIT © 2025 Creator · No warranty

---

# 🌐 AILO–MCP Bridge v1.0 LTS

**자급형 표준 에디션** · MIT 라이선스

---

## 🧭 개요 (한국어)

**AILO–MCP Bridge v1.0 LTS**는 AILO 언어·커널·MCP 프로토콜을 하나의 표준 실행체로 통합한 완결형 버전이다.
AI가 스스로 사고하고, 외부 세계와 안전하게 상호작용할 수 있도록 설계되었다.

> **목표:** AI가 일관되고 검증 가능한 방식으로 사고·행동·검증하도록 하는 자율 언어 체계.

---

### 🔑 주요 특징

* **결정성(Determinism)** — 같은 입력·정책이면 항상 같은 결과
* **추적성(Traceability)** — 모든 결과에 해시·출처 기록
* **정책 기반 안전성** — risk/rule/conf 없이는 실행 불가
* **표준 브리지 계층** — MCP로 검색·API·메모리 연결
* **SDK / CLI / API 제공**

---

### ⚙️ 동작 구조

```
사용자 의도 → AILO 문법 → 브리지 커널 → MCP 계층 → 결과 + 추적정보
```

---

## 🚀 빠른 시작 (Quick Start)

### NodeJS

```bash
npm i @ailo-mcp/bridge
```

```ts
import { Bridge, loadPolicy } from "@ailo-mcp/bridge";

const policy = await loadPolicy("./policies/v1/tenant-kr");
const bridge = new Bridge({ policy });

const plan = {
  intent: { verb: "summarize", obj: "KOSPI 전망", conf: 0.9, risk: "low" }
};

const out = await bridge.run(plan);
console.log(out.result, out.meta.policy_hash, out.trace_id);
```

### Python

```bash
pip install ailo-mcp-bridge
```

```python
from ailo_mcp import Bridge, load_policy

policy = load_policy("./policies/v1/tenant-kr")
b = Bridge(policy=policy)
plan = {"intent":{"verb":"summarize","obj":"KOSPI 전망","conf":0.9,"risk":"low"}}
result = b.run(plan)
print(result["result"], result["meta"]["policy_hash"], result["trace_id"])
```

---

## 🧩 예시 명령어

| 작업         | 자연어 예시                   | 내부 AILO 형태                                                                  |
| ---------- | ------------------------ | --------------------------------------------------------------------------- |
| **요약**     | “오늘 코스피 뉴스 요약해줘.”        | `summarize{obj:"KOSPI news",rule:["tone:analytical"],conf:0.9}!`            |
| **번역**     | “이 문단을 서정 톤으로 영어로 번역해줘.” | `translate{obj:"<text>",to:"en",style:{tone:"lyric"},conf:0.9}!`            |
| **분석**     | “애플과 삼성의 분기 실적 비교해줘.”    | `compare{obj:"Apple vs Samsung profits",rule:["metric:profit"],conf:0.92}!` |
| **검토(성찰)** | “직전 결과의 톤 일관성을 확인해줘.”    | `reflect{obj:"last output",rule:["tone-check"],conf:0.95}.`                 |

---

### 📘 기본 정책

* 접근 범위 제어 (`read:web`, `write:memory`)
* 개인정보 마스킹 (이메일, 전화번호)
* 요청 속도 및 예산 제한
* 모든 결과에 trace ID + policy hash 부여

---

### 📄 라이선스

MIT © 2025 Creator · 보증 없음

---
