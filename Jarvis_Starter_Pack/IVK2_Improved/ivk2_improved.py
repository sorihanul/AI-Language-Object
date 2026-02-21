#!/usr/bin/env python3
"""
IVK2 Improved v0.1
- compact sqlite index
- incremental build
- no raw content storage
- fast local query on signature+tags
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sqlite3
import struct
import time
from collections import Counter
from pathlib import Path
from typing import Iterable

DIM = 12
SEM_DIM = 8
CHUNK_CHARS = 5000
MAX_BYTES = 2_000_000
LEX_TERMS = 10

DEFAULT_EXTS = {
    ".txt", ".md", ".py", ".js", ".ts", ".json", ".yml", ".yaml", ".toml", ".ini", ".cfg",
    ".html", ".css", ".csv", ".log",
}

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".ivk2"}

TOKEN_RE = re.compile(r"[A-Za-z0-9_\-\u3131-\u318E\uAC00-\uD7A3]+")


def stable_hash64(s: str) -> int:
    return int.from_bytes(hashlib.blake2b(s.encode("utf-8", "ignore"), digest_size=8).digest(), "little")


def tokenize(text: str) -> list[str]:
    return [m.group(0).lower() for m in TOKEN_RE.finditer(text)]


def semantic_projection(tokens: Iterable[str]) -> list[float]:
    vec = [0.0] * SEM_DIM
    for t in tokens:
        h = stable_hash64(t)
        d = h % SEM_DIM
        sign = -1.0 if ((h >> 7) & 1) else 1.0
        vec[d] += sign
    return vec


def l2_norm(v: list[float]) -> list[float]:
    s = math.sqrt(sum(x * x for x in v))
    if s <= 1e-12:
        return v
    return [x / s for x in v]


def infer_domain(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in {".py", ".js", ".ts"}:
        return "code"
    if ext in {".json", ".yml", ".yaml", ".toml", ".ini", ".cfg", ".csv"}:
        return "data"
    if ext in {".html", ".css"}:
        return "web"
    if ext in {".md", ".txt", ".log"}:
        return "text"
    return "misc"


def infer_source_type(path: Path) -> str:
    parts = {p.lower() for p in path.parts}
    if "docs" in parts or "documentation" in parts:
        return "docs"
    if "tests" in parts or "test" in parts:
        return "test"
    if "src" in parts:
        return "src"
    return "file"


def freshness(mtime: float) -> float:
    age_days = max(0.0, (time.time() - mtime) / 86400.0)
    return max(0.0, 1.0 - age_days / 365.0)


def reliability(domain: str, source_type: str) -> float:
    base = 0.55
    if domain == "code":
        base += 0.10
    if source_type in {"src", "docs"}:
        base += 0.10
    if source_type == "test":
        base -= 0.05
    return min(1.0, max(0.0, base))


def risk(domain: str) -> float:
    if domain in {"code", "data"}:
        return 0.25
    if domain == "web":
        return 0.30
    return 0.20


def actionability(domain: str) -> float:
    return {
        "code": 0.85,
        "data": 0.65,
        "web": 0.60,
        "text": 0.45,
        "misc": 0.40,
    }.get(domain, 0.40)


def make_signature(text: str, mtime: float, domain: str, source_type: str) -> tuple[list[float], list[str]]:
    tokens = tokenize(text)
    sem = semantic_projection(tokens)
    sem = l2_norm(sem)

    f = freshness(mtime)
    rel = reliability(domain, source_type)
    r = risk(domain)
    act = actionability(domain)

    sig = sem + [f, rel, 1.0 - r, act]
    sig = l2_norm(sig)

    freq = Counter(tokens)
    lex = [t for t, _ in freq.most_common(LEX_TERMS)]
    return sig, lex


def pack_sig(sig: list[float]) -> bytes:
    return struct.pack("<" + "f" * DIM, *sig)


def unpack_sig(buf: bytes) -> list[float]:
    return list(struct.unpack("<" + "f" * DIM, buf))


def cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def connect_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY,
            path TEXT UNIQUE,
            mtime REAL,
            size INTEGER,
            sha1 TEXT,
            domain TEXT,
            source_type TEXT,
            freshness REAL,
            reliability REAL,
            risk REAL,
            actionability REAL,
            sig BLOB,
            lex TEXT,
            updated_at REAL
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_files_domain ON files(domain)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_files_updated ON files(updated_at)")
    return conn


def iter_files(
    root: Path,
    exts: set[str],
    mtime_days_max: float | None = None,
    mtime_days_min: float | None = None,
) -> Iterable[Path]:
    now = time.time()
    for d, dirnames, filenames in os.walk(root):
        dirnames[:] = [x for x in dirnames if x not in SKIP_DIRS]
        for fn in filenames:
            p = Path(d) / fn
            if p.suffix.lower() not in exts:
                continue
            try:
                st = p.stat()
            except OSError:
                continue
            if st.st_size <= 0 or st.st_size > MAX_BYTES:
                continue
            age_days = max(0.0, (now - st.st_mtime) / 86400.0)
            if mtime_days_max is not None and age_days > mtime_days_max:
                continue
            if mtime_days_min is not None and age_days < mtime_days_min:
                continue
            yield p


def read_chunk(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")[:CHUNK_CHARS]


def build_index(
    root: Path,
    db_path: Path,
    exts: set[str],
    remove_missing: bool = True,
    mtime_days_max: float | None = None,
    mtime_days_min: float | None = None,
) -> dict:
    conn = connect_db(db_path)
    cur = conn.cursor()

    seen: set[str] = set()
    inserted = 0
    updated = 0
    skipped = 0

    t0 = time.perf_counter()
    for p in iter_files(root, exts, mtime_days_max=mtime_days_max, mtime_days_min=mtime_days_min):
        st = p.stat()
        path_s = str(p)
        seen.add(path_s)

        row = cur.execute("SELECT mtime,size FROM files WHERE path=?", (path_s,)).fetchone()
        if row and abs(float(row[0]) - st.st_mtime) < 1e-6 and int(row[1]) == st.st_size:
            skipped += 1
            continue

        domain = infer_domain(p)
        src_type = infer_source_type(p)
        text = read_chunk(p)
        sig, lex = make_signature(text, st.st_mtime, domain, src_type)
        sig_b = pack_sig(sig)

        sha1 = hashlib.sha1(path_s.encode("utf-8", "ignore")).hexdigest()
        f = freshness(st.st_mtime)
        rel = reliability(domain, src_type)
        rk = risk(domain)
        act = actionability(domain)

        now = time.time()
        if row:
            cur.execute(
                """
                UPDATE files
                SET mtime=?, size=?, sha1=?, domain=?, source_type=?, freshness=?, reliability=?, risk=?, actionability=?, sig=?, lex=?, updated_at=?
                WHERE path=?
                """,
                (st.st_mtime, st.st_size, sha1, domain, src_type, f, rel, rk, act, sig_b, json.dumps(lex, ensure_ascii=False), now, path_s),
            )
            updated += 1
        else:
            cur.execute(
                """
                INSERT INTO files(path,mtime,size,sha1,domain,source_type,freshness,reliability,risk,actionability,sig,lex,updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (path_s, st.st_mtime, st.st_size, sha1, domain, src_type, f, rel, rk, act, sig_b, json.dumps(lex, ensure_ascii=False), now),
            )
            inserted += 1

    removed = 0
    if remove_missing:
        existing_paths = {r[0] for r in cur.execute("SELECT path FROM files").fetchall()}
        missing = existing_paths - seen
        if missing:
            cur.executemany("DELETE FROM files WHERE path=?", [(m,) for m in missing])
            removed = len(missing)

    conn.commit()
    conn.execute("PRAGMA optimize;")
    conn.close()

    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    db_bytes = db_path.stat().st_size if db_path.exists() else 0
    return {
        "ok": True,
        "root": str(root),
        "db": str(db_path),
        "mtime_days_max": mtime_days_max,
        "mtime_days_min": mtime_days_min,
        "inserted": inserted,
        "updated": updated,
        "skipped": skipped,
        "removed": removed,
        "elapsed_ms": round(elapsed_ms, 2),
        "db_bytes": db_bytes,
    }


def make_query_sig(query: str) -> list[float]:
    q_tokens = tokenize(query)
    sem = l2_norm(semantic_projection(q_tokens))

    # query side operational priors
    q_lower = query.lower()
    q_fresh = 0.70 if any(x in q_lower for x in ["latest", "recent", "최근", "최신"]) else 0.50
    q_rel = 0.80 if any(x in q_lower for x in ["proof", "evidence", "근거", "정확"]) else 0.60
    q_safe = 0.75
    q_act = 0.70 if any(x in q_lower for x in ["how", "implement", "실행", "구현"]) else 0.55

    return l2_norm(sem + [q_fresh, q_rel, q_safe, q_act])


def query_index(db_path: Path, query: str, k: int, domain: str | None, reliability_min: float) -> dict:
    if not db_path.exists():
        return {"ok": False, "error": "index_not_found", "db": str(db_path)}

    conn = connect_db(db_path)
    cur = conn.cursor()

    sql = "SELECT path,domain,source_type,freshness,reliability,risk,actionability,sig,lex FROM files WHERE reliability >= ?"
    params: list[object] = [reliability_min]
    if domain:
        sql += " AND domain = ?"
        params.append(domain)

    rows = cur.execute(sql, tuple(params)).fetchall()
    conn.close()

    qsig = make_query_sig(query)
    qtokens = set(tokenize(query))
    hits = []
    for path, dom, stype, fr, rel, rk, act, sig_b, lex_json in rows:
        sig = unpack_sig(sig_b)
        sim = cosine(qsig, sig)
        score = sim + 0.06 * float(fr) + 0.06 * float(rel) - 0.04 * float(rk) + 0.03 * float(act)
        lex = set(json.loads(lex_json or "[]"))
        overlap = sorted(lex.intersection(qtokens))
        if overlap:
            score += min(0.03, 0.01 * len(overlap))

        hits.append(
            {
                "path": path,
                "score": round(score, 4),
                "domain": dom,
                "source_type": stype,
                "freshness": round(float(fr), 3),
                "reliability": round(float(rel), 3),
                "risk": round(float(rk), 3),
                "overlap": overlap[:5],
            }
        )

    hits.sort(key=lambda x: x["score"], reverse=True)
    top = hits[:k]

    # lightweight relation hints among top hits
    relations = []
    for i in range(len(top)):
        for j in range(i + 1, len(top)):
            if top[i]["domain"] != top[j]["domain"]:
                continue
            relations.append({
                "a": top[i]["path"],
                "b": top[j]["path"],
                "reason": "same_domain",
            })
            if len(relations) >= min(10, k):
                break
        if len(relations) >= min(10, k):
            break

    return {
        "ok": True,
        "query": query,
        "k": k,
        "count": len(top),
        "hits": top,
        "relations": relations,
    }


def query_dual_index(
    hot_db: Path,
    cold_db: Path,
    query: str,
    k: int,
    domain: str | None,
    reliability_min: float,
    hot_weight: float = 1.08,
) -> dict:
    hot = query_index(hot_db, query, max(k * 2, 20), domain, reliability_min)
    cold = query_index(cold_db, query, max(k * 2, 20), domain, reliability_min)

    if not hot.get("ok") and not cold.get("ok"):
        return {
            "ok": False,
            "error": "both_indexes_unavailable",
            "hot_error": hot,
            "cold_error": cold,
        }

    merged: dict[str, dict] = {}

    if hot.get("ok"):
        for h in hot.get("hits", []):
            item = dict(h)
            item["score"] = round(float(item["score"]) * hot_weight, 4)
            item["tier"] = "hot"
            merged[item["path"]] = item

    if cold.get("ok"):
        for c in cold.get("hits", []):
            path = c["path"]
            score = round(float(c["score"]), 4)
            if path not in merged or score > merged[path]["score"]:
                item = dict(c)
                item["score"] = score
                item["tier"] = "cold"
                merged[path] = item

    hits = sorted(merged.values(), key=lambda x: x["score"], reverse=True)[:k]
    return {
        "ok": True,
        "query": query,
        "k": k,
        "hot_db": str(hot_db),
        "cold_db": str(cold_db),
        "hot_weight": hot_weight,
        "count": len(hits),
        "hits": hits,
    }


def stats(db_path: Path) -> dict:
    if not db_path.exists():
        return {"ok": False, "error": "index_not_found", "db": str(db_path)}

    conn = connect_db(db_path)
    cur = conn.cursor()
    total = cur.execute("SELECT COUNT(*) FROM files").fetchone()[0]
    by_domain = cur.execute("SELECT domain, COUNT(*) FROM files GROUP BY domain ORDER BY COUNT(*) DESC").fetchall()
    conn.close()

    return {
        "ok": True,
        "db": str(db_path),
        "db_bytes": db_path.stat().st_size,
        "files": int(total),
        "by_domain": [{"domain": d, "count": int(c)} for d, c in by_domain],
    }


def vacuum(db_path: Path) -> dict:
    if not db_path.exists():
        return {"ok": False, "error": "index_not_found", "db": str(db_path)}
    before = db_path.stat().st_size
    conn = connect_db(db_path)
    conn.execute("VACUUM")
    conn.close()
    after = db_path.stat().st_size
    return {"ok": True, "db": str(db_path), "before": before, "after": after, "saved": before - after}


def main() -> int:
    p = argparse.ArgumentParser(prog="ivk2", description="IVK2 Improved v0.1")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_build = sub.add_parser("build", help="build/update index")
    p_build.add_argument("root")
    p_build.add_argument("--db", default=r"F:\LLM\Output\ivk2\index.sqlite")
    p_build.add_argument("--ext", action="append", default=[])
    p_build.add_argument("--keep-missing", action="store_true")
    p_build.add_argument("--mtime-days-max", type=float, default=None, help="include only files newer than N days")
    p_build.add_argument("--mtime-days-min", type=float, default=None, help="include only files older than N days")

    p_query = sub.add_parser("query", help="query index")
    p_query.add_argument("q")
    p_query.add_argument("--db", default=r"F:\LLM\Output\ivk2\index.sqlite")
    p_query.add_argument("-k", type=int, default=12)
    p_query.add_argument("--domain", default=None)
    p_query.add_argument("--reliability-min", type=float, default=0.0)

    p_qdual = sub.add_parser("query-dual", help="query hot+cold indexes and merge")
    p_qdual.add_argument("q")
    p_qdual.add_argument("--hot-db", default=r"F:\LLM\Output\ivk2\hot.sqlite")
    p_qdual.add_argument("--cold-db", default=r"F:\LLM\Output\ivk2\cold.sqlite")
    p_qdual.add_argument("-k", type=int, default=12)
    p_qdual.add_argument("--domain", default=None)
    p_qdual.add_argument("--reliability-min", type=float, default=0.0)
    p_qdual.add_argument("--hot-weight", type=float, default=1.08)

    p_stats = sub.add_parser("stats", help="index stats")
    p_stats.add_argument("--db", default=r"F:\LLM\Output\ivk2\index.sqlite")

    p_vac = sub.add_parser("vacuum", help="compact sqlite db")
    p_vac.add_argument("--db", default=r"F:\LLM\Output\ivk2\index.sqlite")

    args = p.parse_args()

    if args.cmd == "build":
        exts = {e.lower() if e.startswith(".") else "." + e.lower() for e in args.ext}
        if not exts:
            exts = set(DEFAULT_EXTS)
        res = build_index(
            Path(args.root),
            Path(args.db),
            exts,
            remove_missing=not args.keep_missing,
            mtime_days_max=args.mtime_days_max,
            mtime_days_min=args.mtime_days_min,
        )
    elif args.cmd == "query":
        res = query_index(Path(args.db), args.q, args.k, args.domain, args.reliability_min)
    elif args.cmd == "query-dual":
        res = query_dual_index(
            Path(args.hot_db),
            Path(args.cold_db),
            args.q,
            args.k,
            args.domain,
            args.reliability_min,
            args.hot_weight,
        )
    elif args.cmd == "stats":
        res = stats(Path(args.db))
    elif args.cmd == "vacuum":
        res = vacuum(Path(args.db))
    else:
        res = {"ok": False, "error": "unknown_command"}

    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0 if res.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
