````bash
#!/usr/bin/env bash
# ivk_fast_bootstrap.sh
# Usage:
#   bash ivk_fast_bootstrap.sh
#   python -m pip install -e .
#   ivk build /path/to/root
#   ivk loop "질문을 여기에"

set -euo pipefail

PROJECT="ivk_fast"
mkdir -p "$PROJECT"/ivk_fast/{core,ingest,index,stage1,stage2,policy,runtime}

cat > "$PROJECT/pyproject.toml" <<'TOML'
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "ivk-fast"
version = "0.1.0"
description = "IVK-FAST: Two-stage ultra-fast meaning alignment + doubt loop (agent-first)"
requires-python = ">=3.10"
dependencies = ["numpy>=1.24"]

[project.scripts]
ivk = "ivk_fast.cli:main"
TOML

cat > "$PROJECT/README.md" <<'MD'
# IVK-FAST (v0.1.0)

**Goal:** Stage-1 ranks thousands~tens of thousands of files in ~0.1s (memory-resident 12D signatures).  
Stage-2 performs *oversight* (doubt flags) and requests a refined re-rank. Agent-first.

## Install
```bash
python -m pip install -e .
````

## Build index

```bash
ivk build /path/to/root --out .ivk_index
```

## Run loop

```bash
ivk loop "질문" --index .ivk_index
```

## Notes

* v0.1 indexes **text-like files only** (txt/md/py/json/yaml...).
* Stage-1 never reads file contents at runtime; it uses prebuilt `sig12 + tags`.
* v0.1 uses **hash-projection** (no heavy embedding models) to create 8D semantic component + 4D operational axes.
  MD

cat > "$PROJECT/ivk_fast/**init**.py" <<'PY'
**all** = ["**version**"]
**version** = "0.1.0"
PY

cat > "$PROJECT/ivk_fast/core/types.py" <<'PY'
from **future** import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional

AxisId = Literal[
"Domain","Intent","Abstraction","Scope",
"EvidenceStrength","SourceReliability","Freshness",
"Certainty","Variance","BiasSkew","RiskLevel","Actionability"
]

@dataclass(frozen=True)
class FileRef:
id: str
path: str
mtime: float
size: int
tags: Dict[str, Any]  # domain, reliability, freshness, risk, source_type, ...

@dataclass(frozen=True)
class FileSignature:
id: str
sig12: List[float]           # length 12
tags: Dict[str, Any]         # minimal tags for filter/risk
lex: Optional[List[str]] = None  # tiny sketch for coverage (optional)

@dataclass(frozen=True)
class RankItem:
id: str
score: float
tags: Dict[str, Any]

@dataclass(frozen=True)
class AMF:
query_sig12: List[float]
topk: List[RankItem]
center12: List[float]
density: float
variance: float
skew: float
coverage: Dict[str, Any]

DoubtFlag = Literal[
"COVERAGE_LOW",
"BIAS_RISK",
"CONFLICT_HIGH",
"HIGH_RISK_LOW_CONF",
]

@dataclass(frozen=True)
class OversightResult:
status: Literal["ok","insufficient","high_risk_stop"]
doubt_flags: List[DoubtFlag]
refine_hint: Dict[str, Any]
metrics: Dict[str, float]
PY

cat > "$PROJECT/ivk_fast/core/hashing.py" <<'PY'
from **future** import annotations
import hashlib

def stable_hash64(s: str) -> int:
h = hashlib.blake2b(s.encode("utf-8"), digest_size=8).digest()
return int.from_bytes(h, "little", signed=False)

def stable_id_from_path(path: str) -> str:
# stable-ish id for index; if file moves, id changes (fine for v0.1)
return hashlib.blake2b(path.encode("utf-8"), digest_size=12).hexdigest()
PY

cat > "$PROJECT/ivk_fast/core/timer.py" <<'PY'
from **future** import annotations
import time
from contextlib import contextmanager

@contextmanager
def timed(label: str):
t0 = time.perf_counter()
yield
t1 = time.perf_counter()
print(f"[time] {label}: {(t1-t0)*1000:.2f} ms")
PY

cat > "$PROJECT/ivk_fast/core/config.py" <<'PY'
from **future** import annotations
from dataclasses import dataclass
from typing import List, Set

DEFAULT_EXTS: Set[str] = {
".txt",".md",".py",".js",".ts",".json",".yml",".yaml",".toml",".ini",".cfg",
".html",".css",".csv",".log"
}

@dataclass
class BuildConfig:
root: str
out_dir: str
exts: Set[str]
max_bytes: int = 2_000_000
lex_terms: int = 12          # small sketch terms per file
chunk_chars: int = 4000      # for signature extraction
seed: int = 1337

@dataclass
class RankConfig:
k: int = 120
reliability_min: float = 0.0
freshness_min: float = 0.0
domain_allow: List[str] | None = None
domain_block: List[str] | None = None
diversify_domains: bool = False
diversify_sources: bool = False
PY

cat > "$PROJECT/ivk_fast/ingest/discover.py" <<'PY'
from **future** import annotations
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Set, List

@dataclass(frozen=True)
class FoundFile:
path: str
size: int
mtime: float

def discover_files(root: str, exts: Set[str], max_bytes: int) -> Iterator[FoundFile]:
rootp = Path(root)
for dirpath, dirnames, filenames in os.walk(rootp):
# skip common heavy folders
dn = set(dirnames)
for skip in [".git","node_modules",".venv","venv","**pycache**",".ivk_index"]:
if skip in dn:
dirnames.remove(skip)
for fn in filenames:
p = Path(dirpath) / fn
if p.suffix.lower() not in exts:
continue
try:
st = p.stat()
except OSError:
continue
if st.st_size <= 0 or st.st_size > max_bytes:
continue
yield FoundFile(path=str(p), size=int(st.st_size), mtime=float(st.st_mtime))
PY

cat > "$PROJECT/ivk_fast/ingest/extract.py" <<'PY'
from **future** import annotations
from pathlib import Path

def read_text(path: str) -> str:
p = Path(path)
# v0.1: best-effort utf-8
return p.read_text(encoding="utf-8", errors="ignore")
PY

cat > "$PROJECT/ivk_fast/ingest/chunk.py" <<'PY'
from **future** import annotations

def first_chunk(text: str, max_chars: int) -> str:
text = text.strip()
if len(text) <= max_chars:
return text
return text[:max_chars]
PY

cat > "$PROJECT/ivk_fast/ingest/metadata.py" <<'PY'
from **future** import annotations
from pathlib import Path
from typing import Dict, Any
import time

def infer_domain(path: str) -> str:
p = Path(path)
ext = p.suffix.lower()
if ext in [".py",".js",".ts"]:
return "code"
if ext in [".md",".txt",".log"]:
return "text"
if ext in [".json",".yml",".yaml",".toml",".ini",".cfg",".csv"]:
return "data"
if ext in [".html",".css"]:
return "web"
return "misc"

def source_type(path: str) -> str:
# simple heuristic
p = Path(path)
parts = [x.lower() for x in p.parts]
if "docs" in parts or "documentation" in parts:
return "docs"
if "test" in parts or "tests" in parts:
return "test"
if "src" in parts:
return "src"
return "file"

def compute_freshness(mtime: float) -> float:
# freshness in [0,1], 1 = very recent
now = time.time()
age_days = max(0.0, (now - mtime) / 86400.0)
# 0 days -> 1.0, 365 days -> ~0.0
return max(0.0, 1.0 - (age_days / 365.0))

def compute_reliability(domain: str, stype: str) -> float:
# pragmatic defaults (v0.1)
base = 0.55
if domain == "code":
base += 0.10
if stype in ("docs","src"):
base += 0.10
if stype == "test":
base -= 0.05
return min(1.0, max(0.0, base))

def compute_risk(domain: str) -> float:
# v0.1: low by default
if domain in ("code","data"):
return 0.25
if domain == "web":
return 0.30
return 0.20

def make_tags(path: str, mtime: float) -> Dict[str, Any]:
dom = infer_domain(path)
st = source_type(path)
return {
"domain": dom,
"source_type": st,
"freshness": compute_freshness(mtime),
"reliability": compute_reliability(dom, st),
"risk": compute_risk(dom),
}
PY

cat > "$PROJECT/ivk_fast/index/signature.py" <<'PY'
from **future** import annotations
from dataclasses import dataclass
from typing import List, Tuple
import numpy as np

from ..core.hashing import stable_hash64

# --- IVK 12D axes order (fixed) ---

# 0 Domain

# 1 Intent

# 2 Abstraction

# 3 Scope

# 4 EvidenceStrength

# 5 SourceReliability

# 6 Freshness

# 7 Certainty

# 8 Variance

# 9 BiasSkew

# 10 RiskLevel

# 11 Actionability

def tokenize(text: str) -> List[str]:
# tiny tokenizer
buf = []
w = []
for ch in text.lower():
if ch.isalnum() or ch in "_-":
w.append(ch)
else:
if w:
buf.append("".join(w))
w = []
if w:
buf.append("".join(w))
return buf

def top_terms(tokens: List[str], n: int) -> List[str]:
from collections import Counter
c = Counter(t for t in tokens if len(t) >= 3)
return [t for t, _ in c.most_common(n)]

def hash_projection_semantic8(text: str, seed: int) -> np.ndarray:
"""
v0.1 semantic component:
- hashed token bag projected into 8D deterministically
- no heavy models, fast, stable
"""
toks = tokenize(text)
if not toks:
return np.zeros((8,), dtype=np.float32)

```
# Build sparse hashed counts into 1024 buckets
buckets = 1024
vec = np.zeros((buckets,), dtype=np.float32)
for t in toks:
    h = stable_hash64(f"{seed}:{t}")
    idx = h % buckets
    vec[idx] += 1.0

# deterministic random projection matrix (8 x 1024) generated from seed
rng = np.random.default_rng(seed)
R = rng.standard_normal((8, buckets), dtype=np.float32)
out = (R @ vec).astype(np.float32)

# normalize
norm = np.linalg.norm(out) + 1e-6
return out / norm
```

def operational4(tags: dict) -> np.ndarray:
"""
4D operational axes mapped into slots:
- EvidenceStrength (proxy: length density via tags not available here -> 0.5 baseline)
- SourceReliability (tag)
- Freshness (tag)
- RiskLevel (tag)
"""
evidence = 0.50
rel = float(tags.get("reliability", 0.5))
fresh = float(tags.get("freshness", 0.5))
risk = float(tags.get("risk", 0.2))
return np.array([evidence, rel, fresh, risk], dtype=np.float32)

def make_sig12(text_sample: str, tags: dict, seed: int) -> Tuple[np.ndarray, List[str]]:
sem8 = hash_projection_semantic8(text_sample, seed=seed)

```
# Map sem8 -> conceptual 8 axes (Domain/Intent/Abstraction/Scope + Certainty/Variance/BiasSkew/Actionability)
# v0.1 mapping: simple linear mix (stable). Later you can replace with learned probes.
# Important: we keep it deterministic and cheap.
# sem8 indices: 0..7
domain = sem8[0]
intent = sem8[1]
abstraction = sem8[2]
scope = sem8[3]
certainty = sem8[4]
variance = abs(sem8[5])          # magnitude as conflict proxy (rough)
biasskew = sem8[6]
action = sem8[7]

op4 = operational4(tags)
evidence, reliability, freshness, risk = op4

sig = np.array([
    domain, intent, abstraction, scope,
    evidence, reliability, freshness,
    certainty, variance, biasskew,
    risk, action
], dtype=np.float32)

# squash into [-1,1] (ops are [0,1] so rescale them)
sig[4] = sig[4]*2 - 1
sig[5] = sig[5]*2 - 1
sig[6] = sig[6]*2 - 1
sig[10]= sig[10]*2 - 1

# lex sketch
toks = tokenize(text_sample)
lex = top_terms(toks, n=12)

return sig, lex
```

def make_query_sig12(query: str, seed: int) -> np.ndarray:
# query doesn't have tags; use neutral operational values (0.5)
tags = {"reliability": 0.5, "freshness": 0.5, "risk": 0.2}
sig, _ = make_sig12(query, tags=tags, seed=seed)
return sig
PY

cat > "$PROJECT/ivk_fast/index/store.py" <<'PY'
from **future** import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Iterable, List, Tuple
import json
import numpy as np

@dataclass(frozen=True)
class IndexPaths:
root: str
sig_path: str
meta_path: str

def ensure_dir(p: str) -> None:
Path(p).mkdir(parents=True, exist_ok=True)

def write_jsonl(path: str, rows: Iterable[Dict[str, Any]]) -> None:
with open(path, "w", encoding="utf-8") as f:
for r in rows:
f.write(json.dumps(r, ensure_ascii=False) + "\n")

def read_jsonl(path: str) -> List[Dict[str, Any]]:
out: List[Dict[str, Any]] = []
with open(path, "r", encoding="utf-8") as f:
for line in f:
line = line.strip()
if not line:
continue
out.append(json.loads(line))
return out

def save_index(out_dir: str, ids: List[str], sigs: np.ndarray, meta_rows: List[Dict[str, Any]]) -> IndexPaths:
ensure_dir(out_dir)
sig_path = str(Path(out_dir) / "sig12.memmap")
meta_path = str(Path(out_dir) / "meta.jsonl")

```
# memmap write
mm = np.memmap(sig_path, dtype=np.float32, mode="w+", shape=sigs.shape)
mm[:] = sigs[:]
mm.flush()

write_jsonl(meta_path, meta_rows)

# write ids as first column in meta for alignment safety
# (ids already inside meta_rows; v0.1 assumes stable ordering)
return IndexPaths(root=out_dir, sig_path=sig_path, meta_path=meta_path)
```

def load_index(index_dir: str) -> Tuple[np.memmap, List[Dict[str, Any]]]:
sig_path = str(Path(index_dir) / "sig12.memmap")
meta_path = str(Path(index_dir) / "meta.jsonl")
meta = read_jsonl(meta_path)
n = len(meta)
sigs = np.memmap(sig_path, dtype=np.float32, mode="r", shape=(n,12))
return sigs, meta
PY

cat > "$PROJECT/ivk_fast/index/build.py" <<'PY'
from **future** import annotations
from dataclasses import asdict
from typing import List, Dict, Any
import numpy as np

from ..core.config import BuildConfig
from ..core.hashing import stable_id_from_path
from ..core.timer import timed
from ..ingest.discover import discover_files
from ..ingest.extract import read_text
from ..ingest.chunk import first_chunk
from ..ingest.metadata import make_tags
from ..index.signature import make_sig12
from ..index.store import save_index

def build_index(cfg: BuildConfig) -> str:
ids: List[str] = []
meta_rows: List[Dict[str, Any]] = []
sigs_list: List[np.ndarray] = []

```
with timed("discover"):
    found = list(discover_files(cfg.root, cfg.exts, cfg.max_bytes))
print(f"[build] files={len(found)}")

with timed("extract+signature"):
    for ff in found:
        fid = stable_id_from_path(ff.path)
        tags = make_tags(ff.path, ff.mtime)

        # read once (offline)
        try:
            raw = read_text(ff.path)
        except Exception:
            raw = ""

        sample = first_chunk(raw, cfg.chunk_chars)
        sig12, lex = make_sig12(sample, tags=tags, seed=cfg.seed)

        ids.append(fid)
        sigs_list.append(sig12)

        meta_rows.append({
            "id": fid,
            "path": ff.path,
            "mtime": ff.mtime,
            "size": ff.size,
            "tags": tags,
            "lex": lex[:cfg.lex_terms],
        })

sigs = np.vstack(sigs_list).astype(np.float32) if sigs_list else np.zeros((0,12), dtype=np.float32)

with timed("save_index"):
    paths = save_index(cfg.out_dir, ids=ids, sigs=sigs, meta_rows=meta_rows)

print(f"[build] index_dir={paths.root}")
return paths.root
```

PY

cat > "$PROJECT/ivk_fast/policy/constraints.py" <<'PY'
from **future** import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

@dataclass
class Constraints:
reliability_min: float = 0.0
freshness_min: float = 0.0
domain_allow: Optional[List[str]] = None
domain_block: Optional[List[str]] = None

def pass_constraints(tags: Dict[str, Any], c: Constraints) -> bool:
rel = float(tags.get("reliability", 0.0))
fr  = float(tags.get("freshness", 0.0))
dom = str(tags.get("domain", "misc"))

```
if rel < c.reliability_min:
    return False
if fr < c.freshness_min:
    return False
if c.domain_allow and dom not in c.domain_allow:
    return False
if c.domain_block and dom in c.domain_block:
    return False
return True
```

PY

cat > "$PROJECT/ivk_fast/policy/thresholds.py" <<'PY'
from **future** import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class OversightThresholds:
density_min: float = 0.15
variance_max: float = 0.40
skew_max: float = 0.70
high_risk: float = 0.60
low_certainty: float = 0.15
PY

cat > "$PROJECT/ivk_fast/stage1/ranker.py" <<'PY'
from **future** import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
import numpy as np

from ..core.config import RankConfig
from ..policy.constraints import Constraints, pass_constraints
from ..index.signature import make_query_sig12
from ..stage1.amf import build_amf

def rank_stage1(
query: str,
sigs: np.ndarray,
meta: List[Dict[str, Any]],
seed: int,
cfg: RankConfig,
) -> Tuple[Dict[str, Any], List[int]]:
"""
Returns AMF dict + selected indices
Stage-1 reads ONLY (sigs + meta tags). No file content.
"""
q = make_query_sig12(query, seed=seed).astype(np.float32)

```
c = Constraints(
    reliability_min=cfg.reliability_min,
    freshness_min=cfg.freshness_min,
    domain_allow=cfg.domain_allow,
    domain_block=cfg.domain_block,
)

# hard filter
idxs: List[int] = []
for i, m in enumerate(meta):
    if pass_constraints(m.get("tags", {}), c):
        idxs.append(i)

if not idxs:
    amf = build_amf(q, [], [], seed=seed)
    return amf, []

# vector scoring (dot)
sub = sigs[idxs, :]  # (M,12)
scores = (sub @ q).astype(np.float32)

# pick top-k
k = min(cfg.k, len(idxs))
top_local = np.argpartition(-scores, kth=k-1)[:k]
# sort by score
top_local = top_local[np.argsort(-scores[top_local])]

chosen = [idxs[int(j)] for j in top_local]
chosen_scores = [float(scores[int(j)]) for j in top_local]
chosen_items = [(meta[i]["id"], chosen_scores[n], meta[i].get("tags", {}), sigs[i].tolist()) for n, i in enumerate(chosen)]

amf = build_amf(q, chosen_items, meta, seed=seed)
return amf, chosen
```

PY

cat > "$PROJECT/ivk_fast/stage1/amf.py" <<'PY'
from **future** import annotations
from typing import Any, Dict, List, Tuple
import numpy as np

# chosen_items: List[(id, score, tags, sig12_list)]

def build_amf(query_sig12: np.ndarray, chosen_items: List[Tuple[str,float,dict,list]], meta_all: List[Dict[str,Any]], seed: int) -> Dict[str, Any]:
if not chosen_items:
return {
"query_sig12": query_sig12.tolist(),
"topk": [],
"center12": [0.0]*12,
"density": 0.0,
"variance": 0.0,
"skew": 0.0,
"coverage": {"domains": {}, "sources": {}, "count": 0},
}

```
scores = np.array([s for _, s, _, _ in chosen_items], dtype=np.float32)
sigs = np.array([v for *_, v in chosen_items], dtype=np.float32)  # (K,12)

# weights: softmax-ish on scores (stable)
w = scores - scores.max()
w = np.exp(w).astype(np.float32)
w = w / (w.sum() + 1e-6)

center = (w[:,None] * sigs).sum(axis=0)
# stats
density = float(scores[: min(10, len(scores))].mean())  # simple
variance = float(((sigs - center[None,:])**2).mean())
skew = float(np.linalg.norm(center) / (np.linalg.norm(sigs.mean(axis=0)) + 1e-6))

# coverage: domains & source_types distribution
domains: Dict[str,int] = {}
sources: Dict[str,int] = {}
for _, _, tags, _ in chosen_items:
    d = str(tags.get("domain","misc"))
    s = str(tags.get("source_type","file"))
    domains[d] = domains.get(d,0)+1
    sources[s] = sources.get(s,0)+1

topk = [{"id": fid, "score": float(sc), "tags": tags} for fid, sc, tags, _ in chosen_items]

return {
    "query_sig12": query_sig12.tolist(),
    "topk": topk,
    "center12": center.astype(np.float32).tolist(),
    "density": density,
    "variance": variance,
    "skew": skew,
    "coverage": {"domains": domains, "sources": sources, "count": len(topk)},
}
```

PY

cat > "$PROJECT/ivk_fast/stage2/oversight.py" <<'PY'
from **future** import annotations
from typing import Any, Dict, List
import numpy as np

from ..policy.thresholds import OversightThresholds

# axis indices

IDX_CERTAINTY = 7
IDX_VARIANCE  = 8
IDX_RISK      = 10

def oversight(amf: Dict[str, Any], th: OversightThresholds) -> Dict[str, Any]:
topk = amf.get("topk", [])
center = np.array(amf.get("center12", [0.0]*12), dtype=np.float32)

```
density = float(amf.get("density", 0.0))
variance = float(amf.get("variance", 0.0))
skew = float(amf.get("skew", 0.0))

doubt: List[str] = []
refine: Dict[str, Any] = {}

# coverage check
cov = amf.get("coverage", {})
doms = cov.get("domains", {})
srcs = cov.get("sources", {})
k = int(cov.get("count", 0))

# 1) density
if density < th.density_min:
    doubt.append("COVERAGE_LOW")
    refine["increase_k"] = max(200, k*2 if k else 200)
    refine.setdefault("relax_filters", {})["freshness"] = True

# 2) conflict (variance)
if variance > th.variance_max:
    doubt.append("CONFLICT_HIGH")
    refine.setdefault("tighten_filters", {})["reliability_min"] = 0.65

# 3) bias risk (low diversity + high skew)
diversity_dom = len(doms)
diversity_src = len(srcs)
if (skew > th.skew_max) and (diversity_dom <= 1 or diversity_src <= 1):
    doubt.append("BIAS_RISK")
    refine["diversify"] = {"domains": True, "sources": True}
    refine.setdefault("increase_k", max(250, k*2 if k else 250))

# 4) high-risk low-confidence stop
certainty = float(center[IDX_CERTAINTY])
risk = float(center[IDX_RISK])
# center values are roughly [-1,1]; convert ops: treat <=0 as low
certainty01 = (certainty + 1.0) / 2.0
risk01 = (risk + 1.0) / 2.0
if risk01 >= th.high_risk and certainty01 <= th.low_certainty:
    doubt.append("HIGH_RISK_LOW_CONF")
    return {
        "status": "high_risk_stop",
        "doubt_flags": doubt,
        "refine_hint": refine,
        "metrics": {
            "density": density, "variance": variance, "skew": skew,
            "certainty01": certainty01, "risk01": risk01
        }
    }

status = "ok" if not doubt else "insufficient"
return {
    "status": status,
    "doubt_flags": doubt,
    "refine_hint": refine,
    "metrics": {
        "density": density, "variance": variance, "skew": skew,
        "certainty01": certainty01, "risk01": risk01
    }
}
```

PY

cat > "$PROJECT/ivk_fast/stage2/refine.py" <<'PY'
from **future** import annotations
from typing import Any, Dict
from ..core.config import RankConfig

def apply_refine_hint(cfg: RankConfig, hint: Dict[str, Any]) -> RankConfig:
# returns a NEW config (dataclass-like but RankConfig isn't frozen)
out = RankConfig(
k=cfg.k,
reliability_min=cfg.reliability_min,
freshness_min=cfg.freshness_min,
domain_allow=cfg.domain_allow[:] if cfg.domain_allow else None,
domain_block=cfg.domain_block[:] if cfg.domain_block else None,
diversify_domains=cfg.diversify_domains,
diversify_sources=cfg.diversify_sources,
)

```
if "increase_k" in hint:
    out.k = int(hint["increase_k"])

relax = hint.get("relax_filters", {}) or {}
tighten = hint.get("tighten_filters", {}) or {}

if relax.get("freshness"):
    out.freshness_min = min(out.freshness_min, 0.0)

if "reliability_min" in tighten:
    out.reliability_min = max(out.reliability_min, float(tighten["reliability_min"]))

div = hint.get("diversify", {}) or {}
if div.get("domains"):
    out.diversify_domains = True
if div.get("sources"):
    out.diversify_sources = True

return out
```

PY

cat > "$PROJECT/ivk_fast/runtime/loop.py" <<'PY'
from **future** import annotations
from typing import Any, Dict, List, Tuple
from dataclasses import dataclass
import numpy as np

from ..core.config import RankConfig
from ..policy.thresholds import OversightThresholds
from ..stage1.ranker import rank_stage1
from ..stage2.oversight import oversight
from ..stage2.refine import apply_refine_hint

@dataclass
class LoopResult:
amf: Dict[str, Any]
oversight: Dict[str, Any]
iterations: int

def run_loop(
query: str,
sigs: np.ndarray,
meta: List[Dict[str, Any]],
seed: int,
rank_cfg: RankConfig,
th: OversightThresholds,
max_iters: int = 2,
) -> LoopResult:
cfg = rank_cfg
last_amf: Dict[str, Any] = {}
last_ov: Dict[str, Any] = {}

```
for it in range(max_iters + 1):
    amf, _ = rank_stage1(query, sigs, meta, seed=seed, cfg=cfg)
    ov = oversight(amf, th=th)

    last_amf, last_ov = amf, ov
    if ov["status"] == "ok" or ov["status"] == "high_risk_stop":
        return LoopResult(amf=amf, oversight=ov, iterations=it+1)

    # refine stage1 config (no full-space re-search beyond rank; still rank is O(N) dot but 12D)
    cfg = apply_refine_hint(cfg, ov.get("refine_hint", {}))

return LoopResult(amf=last_amf, oversight=last_ov, iterations=max_iters+1)
```

PY

cat > "$PROJECT/ivk_fast/cli.py" <<'PY'
from **future** import annotations
import argparse
import json
from pathlib import Path

from .core.config import BuildConfig, RankConfig, DEFAULT_EXTS
from .policy.thresholds import OversightThresholds
from .index.build import build_index
from .index.store import load_index
from .stage1.ranker import rank_stage1
from .stage2.oversight import oversight
from .runtime.loop import run_loop

def cmd_build(args: argparse.Namespace) -> int:
cfg = BuildConfig(
root=args.root,
out_dir=args.out,
exts=set(args.exts) if args.exts else DEFAULT_EXTS,
max_bytes=args.max_bytes,
seed=args.seed,
)
build_index(cfg)
return 0

def cmd_rank(args: argparse.Namespace) -> int:
sigs, meta = load_index(args.index)
cfg = RankConfig(
k=args.k,
reliability_min=args.reliability_min,
freshness_min=args.freshness_min,
domain_allow=args.domain_allow,
domain_block=args.domain_block,
)
amf, _ = rank_stage1(args.query, sigs, meta, seed=args.seed, cfg=cfg)
print(json.dumps(amf, ensure_ascii=False, indent=2))
return 0

def cmd_oversight(args: argparse.Namespace) -> int:
# oversight expects AMF json from stdin or file
if args.amf:
amf = json.loads(Path(args.amf).read_text(encoding="utf-8"))
else:
import sys
amf = json.loads(sys.stdin.read())
th = OversightThresholds()
ov = oversight(amf, th=th)
print(json.dumps(ov, ensure_ascii=False, indent=2))
return 0

def cmd_loop(args: argparse.Namespace) -> int:
sigs, meta = load_index(args.index)
rank_cfg = RankConfig(
k=args.k,
reliability_min=args.reliability_min,
freshness_min=args.freshness_min,
domain_allow=args.domain_allow,
domain_block=args.domain_block,
)
th = OversightThresholds()
res = run_loop(
query=args.query,
sigs=sigs,
meta=meta,
seed=args.seed,
rank_cfg=rank_cfg,
th=th,
max_iters=args.max_iters,
)
out = {
"iterations": res.iterations,
"oversight": res.oversight,
"amf": res.amf,
}
print(json.dumps(out, ensure_ascii=False, indent=2))
return 0

def main() -> None:
p = argparse.ArgumentParser(prog="ivk", description="IVK-FAST v0.1")
sub = p.add_subparsers(dest="cmd", required=True)

```
pb = sub.add_parser("build", help="Build index from a root folder")
pb.add_argument("root", help="root directory containing files")
pb.add_argument("--out", default=".ivk_index", help="output index directory")
pb.add_argument("--exts", nargs="*", default=None, help="extensions whitelist (e.g. .md .py)")
pb.add_argument("--max-bytes", type=int, default=2_000_000)
pb.add_argument("--seed", type=int, default=1337)
pb.set_defaults(func=cmd_build)

pr = sub.add_parser("rank", help="Stage-1 rank (outputs AMF)")
pr.add_argument("query")
pr.add_argument("--index", default=".ivk_index")
pr.add_argument("--k", type=int, default=120)
pr.add_argument("--reliability-min", type=float, default=0.0)
pr.add_argument("--freshness-min", type=float, default=0.0)
pr.add_argument("--domain-allow", nargs="*", default=None)
pr.add_argument("--domain-block", nargs="*", default=None)
pr.add_argument("--seed", type=int, default=1337)
pr.set_defaults(func=cmd_rank)

po = sub.add_parser("oversight", help="Stage-2 oversight (reads AMF from stdin or --amf file)")
po.add_argument("--amf", default=None, help="path to AMF json; if omitted reads stdin")
po.set_defaults(func=cmd_oversight)

pl = sub.add_parser("loop", help="Stage-1 -> Stage-2 -> refine -> rerank loop")
pl.add_argument("query")
pl.add_argument("--index", default=".ivk_index")
pl.add_argument("--k", type=int, default=120)
pl.add_argument("--reliability-min", type=float, default=0.0)
pl.add_argument("--freshness-min", type=float, default=0.0)
pl.add_argument("--domain-allow", nargs="*", default=None)
pl.add_argument("--domain-block", nargs="*", default=None)
pl.add_argument("--seed", type=int, default=1337)
pl.add_argument("--max-iters", type=int, default=2)
pl.set_defaults(func=cmd_loop)

args = p.parse_args()
raise SystemExit(args.func(args))
```

if **name** == "**main**":
main()
PY

echo "[ok] Project created: $PROJECT"
echo ""
echo "Next:"
echo "  cd $PROJECT"
echo "  python -m pip install -e ."
echo "  ivk build /path/to/root --out .ivk_index"
echo "  ivk loop "질문" --index .ivk_index"

```
::contentReference[oaicite:0]{index=0}
```
