"""Classical backend — RAM today, phase-change (chalcogenide) memory tomorrow.

Maps the Mnestra logical model onto deterministic digital storage: an exact content-address
table plus a hashed-embedding index for associative recall. This is the *reference* backend
— it actually runs and is what the benchmark and tests exercise. The same code path targets
CMOS phase-change memory (e.g. Ge-Sb-Te), where the "pattern" is a resistance state.
"""
from __future__ import annotations

from .base import Backend, embed, cosine


class ClassicalBackend(Backend):
    name = "classical"
    substrate = "digital RAM / phase-change (GST)"

    def __init__(self) -> None:
        self._store: dict[str, dict] = {}
        self._emb: dict[str, list[float]] = {}

    def write(self, address: str, pattern: dict) -> None:
        self._store[address] = pattern
        text = pattern.get("text") or pattern.get("summary") or str(pattern.get("value", ""))
        self._emb[address] = embed(text)

    def read(self, address: str) -> dict | None:
        return self._store.get(address)

    def query(self, cue: str, k: int = 1) -> list[tuple[str, float]]:
        q = embed(cue)
        scored = sorted(((a, cosine(q, v)) for a, v in self._emb.items()),
                        key=lambda x: x[1], reverse=True)
        return scored[:k]

    def reconstruct(self) -> dict:
        return {"records": len(self._store),
                "addresses": list(self._store.keys()),
                "summaries": {a: (p.get("summary") or p.get("text", ""))[:80]
                              for a, p in self._store.items()}}

    def stats(self) -> dict:
        return {"backend": self.name, "substrate": self.substrate,
                "records": len(self._store), "coherence": "unbounded (refresh/ECC)",
                "read_latency": "ns", "addressing": "exact + associative"}
