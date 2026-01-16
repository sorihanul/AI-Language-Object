"""
MemoryOrchestrator
------------------
Logic layer ("Banker") for lifecycle management of SQLite-backed memories stored via
a provided MemoryManager dependency.

Policy implemented (Promotion & Decay):
1) Consolidation
   - Scan short_term periodically
   - Frequency: if a topic appears > 3 times in the last 24h -> promote to episodic (dedup/merge)
   - Surprise: if importance >= 4 -> immediately promote to long_term (dedup/merge)

2) Decay (Garbage Collection)
   - short_term: if age > 24h and importance < 3 -> delete
   - episodic: if age > 30 days and unreferenced -> archive (or delete)

3) Deduplication
   - On promotion, check similar memory in target tier and merge instead of duplicating

Notes / assumptions:
- MemoryManager API:
    mnemo_add(content, tier, tags, importance) -> new_id (optional)
    mnemo_retrieve(query, tier) -> list[dict] or list[tuple]/list[object]
    mnemo_update(id, **fields) -> None
    mnemo_delete(id) -> None
    mnemo_summary(tier) -> any
- Records from mnemo_retrieve are assumed to contain at least:
    id, content, importance, tags, created_at (or ts)
  If some fields are missing, the orchestrator degrades gracefully.
- "Unreferenced" is tracked via orchestrator-managed metadata inside tags:
    "_refs=<int>", "_last_ref=<iso8601>"
  You can increment references by calling record_reference(memory_id) from your retrieval path.

This file focuses on robust logic and edge-case handling.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple
import math
import re


@dataclass(frozen=True)
class OrchestratorConfig:
    short_term_tier: str = "short_term"
    episodic_tier: str = "episodic"
    long_term_tier: str = "long_term"

    # Optional archival behavior for old episodic memories.
    # If archive_tier is None => delete.
    archive_tier: Optional[str] = "long_term"  # archive by moving into long_term with an "archived" tag

    # Time windows
    freq_window: timedelta = timedelta(hours=24)
    short_term_ttl: timedelta = timedelta(hours=24)
    episodic_ttl: timedelta = timedelta(days=30)

    # Promotion thresholds
    freq_min_count: int = 4          # "appears > 3 times" => at least 4
    surprise_importance: int = 4     # importance >= 4 => immediate long_term

    # Decay threshold
    short_term_delete_importance_lt: int = 3

    # Similarity / dedup tuning
    similarity_threshold: float = 0.82
    max_target_candidates: int = 50  # cap comparisons per promotion to handle high volume

    # Topic signature tuning
    signature_token_limit: int = 10
    min_token_len: int = 3

    # Merge formatting
    merge_separator: str = "\n---\n"


class MemoryOrchestrator:
    """
    Banker/orchestrator for MemoryManager.

    Primary method:
        process_cycle(now=None) -> dict stats

    Optional integration point:
        record_reference(memory_id, now=None)  # call when a memory is "used"
    """

    def __init__(self, memory_manager: Any, config: OrchestratorConfig | None = None):
        self.mm = memory_manager
        self.cfg = config or OrchestratorConfig()

    # ---------------------------
    # Public API
    # ---------------------------

    def process_cycle(self, now: Optional[datetime] = None) -> Dict[str, int]:
        """
        Run one consolidation + decay cycle.

        Returns stats dict with counts of actions performed.
        """
        now = self._ensure_utc(now or datetime.now(timezone.utc))

        stats = {
            "scanned_short_term": 0,
            "promoted_to_long_term": 0,
            "promoted_to_episodic": 0,
            "merged_on_promotion": 0,
            "deleted_short_term": 0,
            "archived_episodic": 0,
            "deleted_episodic": 0,
            "errors": 0,
        }

        try:
            short_memories = self._safe_retrieve_all(self.cfg.short_term_tier)
            stats["scanned_short_term"] = len(short_memories)
        except Exception:
            stats["errors"] += 1
            short_memories = []

        # 1) CONSOLIDATION - Surprise (immediate long_term)
        try:
            surprise_candidates = [
                m for m in short_memories
                if self._get_importance(m) >= self.cfg.surprise_importance
            ]
            for m in surprise_candidates:
                did_merge, did_promote = self._promote_with_dedup(
                    source=m,
                    target_tier=self.cfg.long_term_tier,
                    now=now,
                    add_promotion_tags=["promoted:surprise"],
                )
                if did_promote:
                    stats["promoted_to_long_term"] += 1
                if did_merge:
                    stats["merged_on_promotion"] += 1
        except Exception:
            stats["errors"] += 1

        # Refresh short_term list after surprise promotions (they may have been deleted)
        try:
            short_memories = self._safe_retrieve_all(self.cfg.short_term_tier)
        except Exception:
            stats["errors"] += 1
            short_memories = []

        # 1) CONSOLIDATION - Frequency (topic repeats >3 times in 24h)
        try:
            recent_cutoff = now - self.cfg.freq_window
            recent_short = [
                m for m in short_memories
                if (ts := self._get_created_at(m)) is not None and ts >= recent_cutoff
            ]

            # Group by signature
            buckets: Dict[str, List[Dict[str, Any]]] = {}
            for m in recent_short:
                sig = self._topic_signature(self._get_content(m))
                if not sig:
                    continue
                buckets.setdefault(sig, []).append(m)

            # Promote buckets that meet threshold
            for sig, items in buckets.items():
                if len(items) < self.cfg.freq_min_count:
                    continue

                # Prefer merging the group into a single episodic memory:
                # - Promote the first item, then merge remaining into it via dedup promotion.
                # This minimizes duplicates and DB churn under high volume.
                # Sort by created_at to keep deterministic behavior.
                items_sorted = sorted(items, key=lambda x: self._get_created_at(x) or now)

                for m in items_sorted:
                    did_merge, did_promote = self._promote_with_dedup(
                        source=m,
                        target_tier=self.cfg.episodic_tier,
                        now=now,
                        add_promotion_tags=["promoted:frequency", f"topic:{sig}"],
                        query_hint=sig,
                    )
                    if did_promote:
                        stats["promoted_to_episodic"] += 1
                    if did_merge:
                        stats["merged_on_promotion"] += 1
        except Exception:
            stats["errors"] += 1

        # 2) DECAY - short_term garbage collection
        try:
            short_memories = self._safe_retrieve_all(self.cfg.short_term_tier)
            st_cutoff = now - self.cfg.short_term_ttl
            for m in short_memories:
                ts = self._get_created_at(m)
                if ts is None:
                    # If no timestamp, avoid deleting; conservative.
                    continue
                if ts < st_cutoff and self._get_importance(m) < self.cfg.short_term_delete_importance_lt:
                    if self._safe_delete(self._get_id(m)):
                        stats["deleted_short_term"] += 1
        except Exception:
            stats["errors"] += 1

        # 2) DECAY - episodic archival/deletion
        try:
            episodic = self._safe_retrieve_all(self.cfg.episodic_tier)
            ep_cutoff = now - self.cfg.episodic_ttl
            for m in episodic:
                ts = self._get_created_at(m)
                if ts is None or ts >= ep_cutoff:
                    continue

                refs = self._get_refs(m)
                # Treat missing refs as 0 (unreferenced)
                if refs > 0:
                    continue

                if self.cfg.archive_tier:
                    ok = self._archive_memory(m, now=now)
                    if ok:
                        stats["archived_episodic"] += 1
                else:
                    if self._safe_delete(self._get_id(m)):
                        stats["deleted_episodic"] += 1
        except Exception:
            stats["errors"] += 1

        return stats

    def record_reference(self, memory_id: Any, now: Optional[datetime] = None) -> bool:
        """
        Optional hook: call this when a memory is retrieved/used in your app,
        so episodic unreferenced detection is meaningful.
        """
        now = self._ensure_utc(now or datetime.now(timezone.utc))
        try:
            # We don't know the tier, so try to locate it cheaply by scanning summaries if available,
            # else rely on update-only. This method assumes MemoryManager allows updating by id.
            # We'll store reference metadata in tags.
            self.mm.mnemo_update(memory_id, tags_add=[f"_last_ref={now.isoformat()}", "_refs_inc=1"])
            return True
        except Exception:
            # Fallback: if MemoryManager doesn't support tags_add, try best-effort tags merge.
            try:
                # If mnemo_retrieve can find by id:
                rec = self._find_by_id(memory_id)
                if not rec:
                    return False
                tags = self._get_tags_list(rec)
                tags = self._tags_set_kv(tags, "_last_ref", now.isoformat())
                tags = self._tags_inc_int(tags, "_refs", 1)
                self.mm.mnemo_update(memory_id, tags=tags)
                return True
            except Exception:
                return False

    # ---------------------------
    # Promotion / Dedup / Merge
    # ---------------------------

    def _promote_with_dedup(
        self,
        source: Dict[str, Any],
        target_tier: str,
        now: datetime,
        add_promotion_tags: List[str],
        query_hint: Optional[str] = None,
    ) -> Tuple[bool, bool]:
        """
        Promote `source` into `target_tier` with deduplication:
        - if similar exists in target tier => merge into it, delete source
        - else add new memory in target tier, delete source

        Returns: (did_merge, did_promote_or_merge)
        """
        src_id = self._get_id(source)
        src_content = self._get_content(source)
        if not src_content.strip():
            # Empty content: safest is to delete if it's in short_term; otherwise ignore.
            # We treat this as "no promote".
            return (False, False)

        src_tags = self._get_tags_list(source)
        src_importance = self._get_importance(source)

        # Add promotion tags + ref metadata
        merged_tags = list(src_tags)
        for t in add_promotion_tags:
            if t not in merged_tags:
                merged_tags.append(t)
        merged_tags = self._tags_set_kv(merged_tags, "_last_ref", now.isoformat())
        merged_tags = self._tags_inc_int(merged_tags, "_refs", 1)

        # Find candidate(s) in target tier
        candidates: List[Dict[str, Any]] = []
        try:
            hint = query_hint or self._topic_signature(src_content) or self._query_hint_from_content(src_content)
            candidates = self._safe_retrieve_candidates(target_tier, hint)
        except Exception:
            candidates = []

        # Score similarity
        best = None
        best_score = -1.0
        src_norm = self._normalize_for_similarity(src_content)

        for c in candidates[: self.cfg.max_target_candidates]:
            c_id = self._get_id(c)
            if c_id is None:
                continue
            c_content = self._get_content(c)
            if not c_content.strip():
                continue
            score = self._similarity(src_norm, self._normalize_for_similarity(c_content))
            if score > best_score:
                best_score = score
                best = c

        if best is not None and best_score >= self.cfg.similarity_threshold:
            # MERGE
            target_id = self._get_id(best)
            target_content = self._get_content(best)
            target_tags = self._get_tags_list(best)
            target_importance = self._get_importance(best)

            new_content = self._merge_contents(target_content, src_content)
            new_importance = max(target_importance, src_importance)

            # Merge tags + increment refs
            combined_tags = self._merge_tags(target_tags, merged_tags)
            combined_tags = self._tags_inc_int(combined_tags, "_refs", 1)
            combined_tags = self._tags_set_kv(combined_tags, "_last_ref", now.isoformat())

            self._safe_update(target_id, content=new_content, tags=combined_tags, importance=new_importance)

            # Delete source to avoid duplicates (only if it's not already the same record)
            if src_id is not None and src_id != target_id:
                self._safe_delete(src_id)

            return (True, True)

        # ADD NEW in target tier
        try:
            self.mm.mnemo_add(
                content=src_content,
                tier=target_tier,
                tags=merged_tags,
                importance=src_importance,
            )
            # Delete source after successful add
            if src_id is not None:
                self._safe_delete(src_id)
            return (False, True)
        except Exception:
            # If add fails, do not delete source.
            return (False, False)

    def _archive_memory(self, episodic_rec: Dict[str, Any], now: datetime) -> bool:
        """
        Archive episodic memory:
        - If archive_tier is set: promote to archive_tier with dedup and tag "archived"
          then delete the episodic record.
        - Else: delete.
        """
        if not self.cfg.archive_tier:
            return self._safe_delete(self._get_id(episodic_rec))

        # Mark it archived, do promotion+dedup, but ensure source is removed from episodic.
        did_merge, did_promote = self._promote_with_dedup(
            source=episodic_rec,
            target_tier=self.cfg.archive_tier,
            now=now,
            add_promotion_tags=["archived:episodic", "lifecycle:archive"],
            query_hint=self._topic_signature(self._get_content(episodic_rec)),
        )
        # _promote_with_dedup deletes source on success.
        return did_promote or did_merge

    # ---------------------------
    # Retrieval helpers
    # ---------------------------

    def _safe_retrieve_all(self, tier: str) -> List[Dict[str, Any]]:
        """
        Attempt to retrieve all records for a tier.
        Tries a few common query patterns to accommodate unknown MemoryManager implementations.
        """
        # Prefer a "match all" query; fall back to empty string.
        for q in ("*", "", " "):
            try:
                res = self.mm.mnemo_retrieve(q, tier)
                return self._coerce_records(res)
            except Exception:
                continue
        return []

    def _safe_retrieve_candidates(self, tier: str, query: str) -> List[Dict[str, Any]]:
        """
        Retrieve a bounded candidate set from a tier for dedup checks.
        """
        q = (query or "").strip()
        if not q:
            # If no hint, keep candidates bounded by using a generic token.
            q = "*"
        try:
            res = self.mm.mnemo_retrieve(q, tier)
            return self._coerce_records(res)
        except Exception:
            # Try weaker query
            try:
                res = self.mm.mnemo_retrieve("", tier)
                return self._coerce_records(res)
            except Exception:
                return []

    def _find_by_id(self, memory_id: Any) -> Optional[Dict[str, Any]]:
        """
        Best-effort find by scanning tiers. This is intentionally conservative and limited.
        """
        for tier in (self.cfg.short_term_tier, self.cfg.episodic_tier, self.cfg.long_term_tier):
            try:
                recs = self._safe_retrieve_all(tier)
                for r in recs:
                    if self._get_id(r) == memory_id:
                        return r
            except Exception:
                continue
        return None

    # ---------------------------
    # Update/Delete helpers
    # ---------------------------

    def _safe_update(self, memory_id: Any, **fields: Any) -> bool:
        if memory_id is None:
            return False
        try:
            self.mm.mnemo_update(memory_id, **fields)
            return True
        except Exception:
            return False

    def _safe_delete(self, memory_id: Any) -> bool:
        if memory_id is None:
            return False
        try:
            self.mm.mnemo_delete(memory_id)
            return True
        except Exception:
            return False

    # ---------------------------
    # Record coercion / field getters
    # ---------------------------

    def _coerce_records(self, res: Any) -> List[Dict[str, Any]]:
        """
        Coerce results into list[dict]. Supports:
          - list[dict]
          - list[tuple] (id, content, tier, tags, importance, created_at, ...)
          - list[object] with attributes
        """
        if not res:
            return []
        if isinstance(res, list) and all(isinstance(x, dict) for x in res):
            return res  # type: ignore[return-value]

        out: List[Dict[str, Any]] = []
        if isinstance(res, list):
            for x in res:
                if isinstance(x, dict):
                    out.append(x)
                elif isinstance(x, (tuple, list)):
                    # Best effort mapping by common ordering
                    d: Dict[str, Any] = {}
                    if len(x) > 0:
                        d["id"] = x[0]
                    if len(x) > 1:
                        d["content"] = x[1]
                    if len(x) > 2:
                        d["tier"] = x[2]
                    if len(x) > 3:
                        d["tags"] = x[3]
                    if len(x) > 4:
                        d["importance"] = x[4]
                    if len(x) > 5:
                        d["created_at"] = x[5]
                    out.append(d)
                else:
                    # object with attrs
                    d = {}
                    for k in ("id", "content", "tier", "tags", "importance", "created_at", "ts"):
                        if hasattr(x, k):
                            d[k] = getattr(x, k)
                    out.append(d)
        return out

    def _get_id(self, rec: Dict[str, Any]) -> Any:
        return rec.get("id", rec.get("_id"))

    def _get_content(self, rec: Dict[str, Any]) -> str:
        c = rec.get("content") or rec.get("text") or ""
        return str(c)

    def _get_importance(self, rec: Dict[str, Any]) -> int:
        v = rec.get("importance", rec.get("score", 0))
        try:
            return int(v)
        except Exception:
            return 0

    def _get_created_at(self, rec: Dict[str, Any]) -> Optional[datetime]:
        raw = rec.get("created_at", rec.get("ts", rec.get("timestamp")))
        if raw is None:
            return None
        if isinstance(raw, datetime):
            return self._ensure_utc(raw)
        if isinstance(raw, (int, float)):
            # assume unix seconds
            try:
                return datetime.fromtimestamp(float(raw), tz=timezone.utc)
            except Exception:
                return None
        if isinstance(raw, str):
            # parse ISO8601-ish
            s = raw.strip()
            try:
                dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
                return self._ensure_utc(dt)
            except Exception:
                return None
        return None

    def _get_tags_list(self, rec: Dict[str, Any]) -> List[str]:
        tags = rec.get("tags", [])
        if tags is None:
            return []
        if isinstance(tags, list):
            return [str(x) for x in tags if str(x).strip()]
        if isinstance(tags, str):
            # support comma-separated
            parts = [p.strip() for p in tags.split(",")]
            return [p for p in parts if p]
        # unknown type
        try:
            return [str(tags)]
        except Exception:
            return []

    # ---------------------------
    # Reference metadata in tags
    # ---------------------------

    def _get_refs(self, rec: Dict[str, Any]) -> int:
        tags = self._get_tags_list(rec)
        for t in tags:
            if t.startswith("_refs="):
                try:
                    return int(t.split("=", 1)[1])
                except Exception:
                    return 0
        return 0

    def _tags_set_kv(self, tags: List[str], key: str, value: str) -> List[str]:
        """
        Set/replace "key=value" tag. Removes any existing key=... occurrences.
        """
        prefix = f"{key}="
        new_tags = [t for t in tags if not t.startswith(prefix)]
        new_tags.append(f"{key}={value}")
        return self._dedup_tags(new_tags)

    def _tags_inc_int(self, tags: List[str], key: str, inc: int) -> List[str]:
        """
        Increment int tag "key=<int>". If missing, create.
        """
        prefix = f"{key}="
        cur = 0
        new_tags = []
        found = False
        for t in tags:
            if t.startswith(prefix):
                found = True
                try:
                    cur = int(t.split("=", 1)[1])
                except Exception:
                    cur = 0
            else:
                new_tags.append(t)
        new_tags.append(f"{key}={cur + inc}")
        return self._dedup_tags(new_tags)

    def _merge_tags(self, a: List[str], b: List[str]) -> List[str]:
        """
        Merge tag lists with basic normalization. For conflicting kv tags, prefer 'b' values.
        """
        # Build kv from a, then overwrite with b kv
        kv: Dict[str, str] = {}
        plain: List[str] = []

        def ingest(ts: List[str], overwrite: bool):
            for t in ts:
                if "=" in t and not t.startswith("http"):
                    k, v = t.split("=", 1)
                    k = k.strip()
                    v = v.strip()
                    if not k:
                        continue
                    if overwrite or k not in kv:
                        kv[k] = v
                else:
                    if t not in plain:
                        plain.append(t)

        ingest(a, overwrite=False)
        ingest(b, overwrite=True)

        merged = plain + [f"{k}={v}" for k, v in kv.items()]
        return self._dedup_tags(merged)

    def _dedup_tags(self, tags: List[str]) -> List[str]:
        seen = set()
        out = []
        for t in tags:
            tt = str(t).strip()
            if not tt or tt in seen:
                continue
            seen.add(tt)
            out.append(tt)
        return out

    # ---------------------------
    # Topic signature / similarity
    # ---------------------------

    def _topic_signature(self, content: str) -> str:
        """
        Create a lightweight topic signature for frequency counting.
        Uses top tokens (by length) after normalization, to be stable across repeats.
        """
        toks = self._tokenize(content)
        if not toks:
            return ""
        # Prefer longer tokens to capture meaning; cap token count
        toks = sorted(set(toks), key=lambda x: (-len(x), x))
        toks = toks[: self.cfg.signature_token_limit]
        return "_".join(toks)

    def _query_hint_from_content(self, content: str) -> str:
        toks = self._tokenize(content)
        return " ".join(toks[: min(6, len(toks))]) if toks else ""

    def _normalize_for_similarity(self, text: str) -> str:
        t = text.lower()
        t = re.sub(r"\s+", " ", t).strip()
        return t

    def _tokenize(self, text: str) -> List[str]:
        t = text.lower()
        # Keep words/numbers; drop punctuation
        raw = re.findall(r"[a-z0-9]+", t)
        toks = [w for w in raw if len(w) >= self.cfg.min_token_len]
        # Remove ultra-common stop-ish tokens without importing a stopword list
        common = {"the", "and", "for", "with", "that", "this", "from", "are", "was", "were", "you", "your", "but"}
        toks = [w for w in toks if w not in common]
        return toks

    def _similarity(self, a_norm: str, b_norm: str) -> float:
        """
        Hybrid similarity:
        - Token Jaccard
        - Character 3-gram Jaccard
        Combine with weights; designed to be cheap and robust without external deps.
        """
        if a_norm == b_norm:
            return 1.0
        if not a_norm or not b_norm:
            return 0.0

        a_t = set(self._tokenize(a_norm))
        b_t = set(self._tokenize(b_norm))
        tj = self._jaccard(a_t, b_t)

        a_g = set(self._char_ngrams(a_norm, 3))
        b_g = set(self._char_ngrams(b_norm, 3))
        gj = self._jaccard(a_g, b_g)

        # Weight tokens slightly more
        score = 0.6 * tj + 0.4 * gj
        # Clamp
        return max(0.0, min(1.0, score))

    def _char_ngrams(self, s: str, n: int) -> Iterable[str]:
        s = re.sub(r"\s+", " ", s).strip()
        if len(s) < n:
            return [s] if s else []
        return (s[i : i + n] for i in range(len(s) - n + 1))

    def _jaccard(self, a: set, b: set) -> float:
        if not a and not b:
            return 1.0
        if not a or not b:
            return 0.0
        inter = len(a & b)
        union = len(a | b)
        return inter / union if union else 0.0

    def _merge_contents(self, existing: str, incoming: str) -> str:
        """
        Merge content while avoiding runaway growth from repeated merges.
        Strategy:
          - If incoming is already contained, keep existing.
          - Else append with separator.
          - Soft cap by truncating very large strings (keeps tail+head).
        """
        ex = existing.strip()
        inc = incoming.strip()
        if not inc:
            return ex
        if not ex:
            return inc
        if inc in ex:
            return ex

        merged = f"{ex}{self.cfg.merge_separator}{inc}"

        # Soft cap: ~20k chars (tunable). Keep both ends to preserve context.
        cap = 20000
        if len(merged) > cap:
            head = merged[: int(cap * 0.6)]
            tail = merged[-int(cap * 0.4) :]
            merged = head + self.cfg.merge_separator + "[...truncated...]" + self.cfg.merge_separator + tail
        return merged

    # ---------------------------
    # Time utilities
    # ---------------------------

    def _ensure_utc(self, dt: datetime) -> datetime:
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
