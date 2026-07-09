"""A deterministic stand-in LLM with an explicit cost model.

It is NOT a transformer — it is a faithful model of the *cost structure* that makes the
Mnestra approach efficient, so the benchmark numbers come from the real mechanism rather than
a hand-wave:

  * `work` accumulates the number of context tokens processed per call. Attention cost grows
    with context length, so total work is a defensible proxy for FLOPs / latency / $$.
  * content-addressed `memo` lets identical sub-derivations be reused instead of recomputed —
    a global, position-independent KV-cache, which is exactly what Mnestra's content addressing
    enables across calls and across parallel workers.
"""
from __future__ import annotations

from .backends.base import content_address


class MockLLM:
    def __init__(self) -> None:
        self.work = 0          # total context tokens processed (proxy for compute)
        self.calls = 0         # generation calls
        self.recomputes = 0    # derivations done that a memo could have served
        self.memo: dict[str, str] = {}

    def _toks(self, text: str) -> int:
        return len(text.split())

    def generate(self, context: str, memo_key: str | None = None) -> str:
        """Generate from `context`. If `memo_key` is given and seen before, the result is
        served from content-addressed memory at ~zero compute (cache hit)."""
        if memo_key is not None and memo_key in self.memo:
            return self.memo[memo_key]            # content-addressed hit — no work charged
        self.calls += 1
        self.work += self._toks(context)
        out = f"<gen:{content_address(context)[:10]}>"
        if memo_key is not None:
            self.memo[memo_key] = out
        return out

    def derive_fact(self, fact: str, memoized: bool) -> str:
        """Derive a shared fact. With Mnestra it is content-addressed and derived once;
        without it, the same fact is re-derived at every use."""
        key = content_address(("fact", fact))
        if memoized and key in self.memo:
            return self.memo[key]
        self.calls += 1
        self.work += self._toks(fact) + 4         # derivation cost
        if not memoized:
            self.recomputes += 1
        out = f"<fact:{key[:8]}>"
        self.memo[key] = out
        return out

    def snapshot(self) -> dict:
        return {"work_tokens": self.work, "calls": self.calls, "recomputes": self.recomputes}
