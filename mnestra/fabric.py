"""Mnestra Inference Fabric (AIF) — a new memory model that COMPOSES the proven industrial
inference-efficiency stack on one content-addressed, substrate-agnostic substrate.

It does not replace KV caching, prompt caching, RAG, speculative decoding, or MoE routing.
It *unifies* them: each is a tier over the same Backend (classical today; photonic/quantum
forward-compatible), keyed by content address, so the techniques share storage, dedup against
one another, and inherit substrate portability.

  Tier            Industrial concept it builds on               Mnestra's additive contribution
  ----            -------------------------------               -----------------------------
  L0 KV pages     PagedAttention / vLLM                         content-keyed pages -> cross-request dedup + prefix sharing
  L1 prefix cache prompt caching (Anthropic / vLLM APC)         BLAKE2b prefix addressing = caching, generalized
  L2 working set  (novel) Mnestra Codex "whole-book" view         bounded structure-complete context
  L3 long-term    RAG over ANN (FAISS / HNSW)                   associative recall on the SAME store
  router          MoE-style routing                             serve from the cheapest competent tier
  integrity       Merkle DAG / IPFS content addressing          dedup + integrity for free
  persistence     LSM-style tiering                             classical -> photonic -> quantum

Everything below is runnable and the demo metrics (hit/dedup ratios) are computed from the
workload — they are real cache behavior, NOT modeled LLM speedups.
"""
from __future__ import annotations

from .backends.base import Backend, content_address
from .backends import ClassicalBackend

PAGE = 16  # tokens per KV page (PagedAttention-style fixed blocks)


class KVPageStore:
    """L0 — paged attention cache, content-addressed so identical pages (e.g. a shared system
    prompt across requests) are stored once. Mirrors vLLM PagedAttention + automatic prefix
    sharing, but the page id is the content hash, so dedup is global, not per-sequence."""

    def __init__(self) -> None:
        self.pages: dict[str, list[str]] = {}
        self.logical_writes = 0

    def write_sequence(self, tokens: list[str]) -> list[str]:
        addrs = []
        for i in range(0, len(tokens), PAGE):
            page = tokens[i:i + PAGE]
            addr = content_address(page)
            self.logical_writes += 1
            self.pages.setdefault(addr, page)
            addrs.append(addr)
        return addrs

    def dedup_ratio(self) -> float:
        return round(self.logical_writes / max(1, len(self.pages)), 3)


class PrefixCache:
    """L1 — prompt/prefix caching. A request's leading tokens are content-addressed; a hit
    means the prefix's compute is reused. This is exactly prompt caching, expressed in the
    same address space as everything else."""

    def __init__(self) -> None:
        self.seen: set[str] = set()
        self.hits = 0
        self.misses = 0

    def lookup(self, prefix_tokens: list[str]) -> bool:
        addr = content_address(prefix_tokens)
        if addr in self.seen:
            self.hits += 1
            return True
        self.seen.add(addr)
        self.misses += 1
        return False

    def hit_rate(self) -> float:
        n = self.hits + self.misses
        return round(self.hits / n, 3) if n else 0.0


class Fabric:
    """The unified inference fabric. One Backend underneath every tier."""

    def __init__(self, backend: Backend | None = None) -> None:
        self.backend = backend or ClassicalBackend()   # swap for photonic/quantum, unchanged
        self.kv = KVPageStore()
        self.prefix = PrefixCache()
        self.tiers_served: dict[str, int] = {"prefix_cache": 0, "kv_dedup": 0,
                                              "retrieval": 0, "generate": 0}

    def ingest(self, text: str, summary: str = "") -> str:
        """Persist a document into L3 (RAG store) on the content-addressed backend."""
        addr = content_address(text)
        self.backend.write(addr, {"text": text, "summary": summary or text[:60]})
        return addr

    def serve(self, request: dict) -> dict:
        """MoE-style router: satisfy a request from the cheapest competent tier.

        request = {prefix: [tokens], body: [tokens], query: str|None}
        """
        plan = []
        # L1 prefix cache
        if self.prefix.lookup(request.get("prefix", [])):
            plan.append("prefix_cache"); self.tiers_served["prefix_cache"] += 1
        # L0 KV page dedup
        before = len(self.kv.pages)
        self.kv.write_sequence(request.get("prefix", []) + request.get("body", []))
        if len(self.kv.pages) == before:
            plan.append("kv_dedup"); self.tiers_served["kv_dedup"] += 1
        # L3 retrieval (RAG) when a semantic query is present
        q = request.get("query")
        if q:
            hits = self.backend.query(q, k=3)
            if hits and hits[0][1] > 0:
                plan.append("retrieval"); self.tiers_served["retrieval"] += 1
        if not plan:
            plan.append("generate"); self.tiers_served["generate"] += 1
        return {"served_by": plan}

    def stats(self) -> dict:
        return {
            "substrate": self.backend.stats().get("substrate"),
            "prefix_hit_rate": self.prefix.hit_rate(),
            "kv_pages_physical": len(self.kv.pages),
            "kv_pages_logical": self.kv.logical_writes,
            "kv_dedup_ratio": self.kv.dedup_ratio(),
            "tiers_served": self.tiers_served,
        }


def demo() -> dict:
    """A workload of requests that share a big system prompt and overlapping bodies — the
    common real case — plus a few retrievals. Metrics are computed from the run."""
    fab = Fabric()
    for i in range(5):
        fab.ingest(f"doc {i} about photonic and quantum memory substrates", f"doc{i}")

    system = [f"sys{w}" for w in range(48)]          # shared 48-token system prompt
    served = []
    for i in range(40):
        body = [f"u{i}_{w}" for w in range(20)]      # per-request unique body
        # every 3rd request repeats an earlier body verbatim (tool templates, retries, etc.)
        if i % 3 == 0 and i > 0:
            body = [f"u{i-3}_{w}" for w in range(20)]
        q = "quantum memory" if i % 5 == 0 else None
        served.append(fab.serve({"prefix": system, "body": body, "query": q}))
    return fab.stats()


def main() -> None:
    import json
    print("Mnestra Inference Fabric — composing the industrial stack on one content-addressed substrate\n")
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
