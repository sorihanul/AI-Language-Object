# 🌐 **AILO–MCP Bridge v1.0 LTS — Self-Contained Standard Edition**

> **Status:** Stable · Long-Term Support (24 months)
> **Scope:** AILO ↔ MCP Unified Protocol · Core Runtime · SDK · CLI · Policy-as-Code
> **Mission:** *To enable AI systems to think in their own language and interact with the world through a unified, verifiable protocol.*

---

## 0️⃣ Core Principles

1. **Determinism** — Same input + policy + version → identical output.
2. **Traceability** — Every decision must be provable by hash, policy, and source.
3. **Safety** — No action-type output without explicit `rule`, `risk`, and `conf`.
4. **Autonomy** — All external operations use standardized MCP interfaces.
5. **Integrity** — Schemas, policies, and tools operate only as signed bundles.

---

## 1️⃣ Core Architecture

```
User Intent → AILO Grammar → Bridge Kernel → MCP Layer
                           ↓
                    Tools / APIs / Memory
```

| Layer              | Description                                                 |
| ------------------ | ----------------------------------------------------------- |
| **AILO Grammar**   | Semantic + rule + emotion syntax for AI reasoning           |
| **Bridge Kernel**  | Pipeline: Sense → Plan → Policy → Tool → Validate → Reflect |
| **MCP Layer**      | Standard connectors for external data and tools             |
| **Reflexive Core** | Self-healing, quality learning, and validation loops        |

---

## 2️⃣ Canonical AILO Schema

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

### 📦 JavaScript / TypeScript SDK

```bash
npm i @ailo-mcp/bridge
```

```ts
import { Bridge, loadPolicy } from "@ailo-mcp/bridge";

const policy = await loadPolicy("./policies/v1/tenant-kr");
const bridge = new Bridge({ policy, tenant:{org:"alpha",id:"t-kr",project:"p-news"} });

const plan = {
  intent:{ verb:"summarize", obj:"KOSPI flow", rule:["tone:analytical","len:mid"], conf:0.9, risk:"low" },
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
plan = {"intent":{"verb":"summarize","obj":"KOSPI flow","rule":["tone:analytical","len:mid"],"conf":0.9,"risk":"low"}}
result = b.run(plan)
print(result["result"], result["meta"]["policy_hash"], result["trace_id"])
```

### 💻 Command-Line Interface

```bash
npx ailo-mcp run --topic "KOSPI outlook" --sources 5 --min-agree 0.6 \
  --tenant t-kr --policy ./policies/v1/tenant-kr
```

---

## 4️⃣ Core Runtime Components

| Layer                | Key Responsibilities                               |
| -------------------- | -------------------------------------------------- |
| **Planner**          | Parse AILO intent → deterministic execution plan   |
| **Policy Engine**    | Verify scope, domain, PII, and quota rules         |
| **Sandbox**          | Time/memory/domain restrictions for safe execution |
| **Consensus Kernel** | Parallel sourcing → weighted trust aggregation     |
| **Validator**        | SRM, AffSRM, safety, and explainability checks     |
| **Memory**           | Semantic storage, retrieval, and self-healing      |
| **Trace System**     | `hash_chain + policy_hash + schema_id` provenance  |
| **Bridge SDK**       | LTS API with deterministic async interface         |
| **CLI / Dashboard**  | Real-time monitoring and audit view                |

---

## 5️⃣ Deployment Guidelines

* **Tenant Model:** single or isolated multi-tenant (separate keys + folders).
* **Policy Bundles:** YAML + signed JSON manifest.
* **Logging:** JSONL + OTLP export for dashboards.
* **Cache TTL:** 1800 s; key = `H(intent,policy_hash,VERSION)`.
* **Service SLO:** availability ≥ 99.5 %, p95 < 2.5 s, SRM ≥ 0.95.

---

## 6️⃣ Reference Dashboard Widgets

* Bridge Throughput / Latency (p50-p95-p99)
* Consensus Agreement % / Self-Heal Rate / SRM Distribution
* Cache Hit Ratio / Cost per Request / Policy Hash Performance
* Circuit State / Error-Budget Usage / Tenant Isolation Metrics

---

## 7️⃣ LTS Operational Charter

* **Immutable Builds:** every executable = verified artifact hash.
* **Signed Policies:** pre-execution signature verification.
* **Audit Trail:** append-only logs with `policy_hash` and `trace_id`.
* **Compliance:** GDPR-aligned PII masking + region pinning by default.
* **Chaos Tests:** automated monthly injection, recovery rate ≥ 0.9.

---

### 🔖 Concept Summary

**AILO–MCP Bridge v1.0 LTS** unifies:

* **Language (AILO)** · **Protocol (MCP)** · **Policy (Pac)** · **Tool SDKs** · **Operational Standard**
  into a **single, self-contained ecosystem**.
  It enables an AI system to think, act, and verify autonomously—without dependence on any external platform.

---

### 🪶 Reflection Note

> Completion is not closure,
> but the point where every path speaks the same grammar.
> **v1.0 LTS is the self-sufficient language state of AILO.**
