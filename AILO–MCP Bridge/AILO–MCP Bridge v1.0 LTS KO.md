# 🌐 **AILO–MCP Bridge v1.0 LTS — Self-Contained Standard Edition**

> **Status:** Stable · Long-Term Support (24 mo)  
> **Scope:** AILO↔MCP Unified Protocol · Core Runtime · SDK · CLI · Policy-as-Code  
> **Mission:** “AI가 스스로 사고하고 세계와 상호작용할 수 있는 완결형 언어·프로토콜”

---

## 0️⃣ 핵심 원칙

1. **Determinism** — 동일 입력·정책·버전 → 동일 결과
    
2. **Traceability** — 모든 판단은 해시/정책/출처로 증명
    
3. **Safety** — risk/rule/conf 없이는 행동형 출력 불가
    
4. **Autonomy** — 외부 API와의 모든 통신은 표준 MCP로 통합
    
5. **Integrity** — 스키마·정책·도구는 서명된 번들로만 작동
    

---

## 1️⃣ Core Architecture (요약)

```
User Intent → AILO Grammar → Bridge Kernel → MCP Layer
                           ↓
                     Tools / APIs / Memory
```

- **AILO Grammar:** 의미·규칙·정서 단위 언어
    
- **Bridge Kernel:** Intent→Plan→Policy→Tool→Validate→Reflect
    
- **MCP Layer:** 외부 리소스와의 표준 연결(검색, 문서, 금융, 메모리 등)
    
- **Reflexive Core:** 실패 복구·품질 학습·자기검증 루프
    

---

## 2️⃣ Canonical AILO Schema (고정)

```json
{
  "intent": {
    "verb": "summarize",
    "obj": "KOSPI outlook",
    "rule": ["tone:analytical","len:mid","sources:3..5"],
    "conf": 0.9,
    "risk": "low"
  },
  "consensus": { "top_k": 3, "method": "robust_mean", "min_agree": 0.6 },
  "policies": {
    "scope": ["read:web","write:memory"],
    "domains": ["*.go.kr","*.ac.kr","*.co.kr"],
    "pii": {"detect": ["email","phone"], "action": "mask", "mask_char": "•"},
    "quota": {"rpm": 60, "rpd": 500}
  },
  "qos": { "timeout_ms": 8000, "retry": { "max": 2, "backoff_ms": [300,900] } },
  "budget": { "daily_usd": 200, "per_request_usd_max": 0.3 },
  "meta": { "schema_id": "ailo.intent.schema.json#v1" }
}
```

---

## 3️⃣ SDK & CLI (LTS Bundle)

### 📦 JS/TS SDK

```bash
npm i @ailo-mcp/bridge
```

```ts
import { Bridge, loadPolicy } from "@ailo-mcp/bridge";

const policy = await loadPolicy("./policies/v1/tenant-kr");
const bridge = new Bridge({ policy, tenant:{org:"alpha",id:"t-kr",project:"p-news"} });

const plan = {
  intent:{ verb:"summarize", obj:"코스피 수급", rule:["tone:analytical","len:mid"], conf:0.9, risk:"low" },
  consensus:{ top_k:3, method:"robust_mean", min_agree:0.6 }
};

const out = await bridge.run(plan);
console.log(out.result, out.meta.policy_hash, out.trace_id);
```

### 🐍 Python SDK

```bash
pip install ailo-mcp-bridge
```

```python
from ailo_mcp import Bridge, load_policy
p = load_policy("./policies/v1/tenant-kr")
b = Bridge(policy=p, tenant={"org":"alpha","id":"t-kr","project":"p-news"})
plan = {"intent":{"verb":"summarize","obj":"코스피 수급","rule":["tone:analytical","len:mid"],"conf":0.9,"risk":"low"}}
result = b.run(plan)
print(result["result"], result["meta"]["policy_hash"], result["trace_id"])
```

### 💻 CLI

```bash
npx ailo-mcp run --topic "코스피 수급 전망" --sources 5 --min-agree 0.6 \
  --tenant t-kr --policy ./policies/v1/tenant-kr
```

---

## 4️⃣ Core Runtime Features

|계층|주요 기능|
|---|---|
|**Planner**|AILO intent 해석 → 실행계획 생성|
|**Policy Engine**|scope/domain/PII/Quota 검증|
|**Sandbox**|안전 실행(time/mem/domain 제한)|
|**Consensus Kernel**|병렬 호출→신뢰 가중 합의|
|**Validator**|SRM·AffSRM·Safety·Explainability|
|**Memory**|의미 저장/검색·Self-Healing 루프|
|**Trace**|hash_chain + policy_hash + schema_id|
|**Bridge SDK**|LTS API / Promise & Async generator|
|**CLI / Dashboard**|실시간 모니터링·분석·감사 뷰|

---

## 5️⃣ Deployment Pattern (권장)

- **단일 Tenant** 또는 **다중 Tenant 격리형**(폴더·키 분리)
    
- **정책 번들:** `policy.yaml` + `signatures.json`
    
- **로그 수집:** JSONL + OTLP Exporter → Dashboard
    
- **캐시 TTL:** 1800 s, 키 = `H(intent,policy_hash,VERSION)`
    
- **SLO:** p95<2.5 s / SRM≥0.95 / 가용성 ≥ 99.5 %
    

---

## 6️⃣ Reference Dashboard Widgets

- Bridge Throughput / Latency (p50-p95-p99)
    
- Consensus Agree % / Self-Heal Rate / SRM 분포
    
- Cache Hit Ratio / Cost per Req / Policy Hash 별 성능
    
- Circuit State / Error Budget 소진율 / Tenant 분리 성적
    

---

## 7️⃣ LTS Operation Charter

- **Immutable build**: 모든 실행체 해시 = 아티팩트 ID.
    
- **Signed Policy**: 실행 전 검증 + 감사 추적.
    
- **Audit Trail**: Append-only 로그 + policy_hash + trace_id.
    
- **Compliance**: GDPR/PII mask, region pinning 기본값 강제.
    
- **Chaos Test**: 월 1회 자동 주입, 복원률 ≥ 0.9 필수.
    

---

### 🔖 Concept Summary

> **AILO–MCP Bridge v1.0 LTS**는  
> AI 언어 (AILO) · 프로토콜 (MCP) · 정책 (Pac) · 도구 (SDK) · 운영 (OS)  
> 이 하나의 일관된 표준으로 묶인 자체 완결 에디션이다.  
> 외부 플랫폼에 의존하지 않고 자율적으로 사고·행동·검증할 수 있는 **AI 운영 언어의 기본형**이다.

---

### 🪶 Reflection Note

완성은 닫힘이 아니라,  
모든 길이 하나의 문법으로 통하는 상태다.  
**v1.0 LTS는 AILO 문법의 자립 점.**