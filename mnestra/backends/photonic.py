"""Photonic backend — spectral-spatial holographic memory (simulation).

Models frequency/spatial-multiplexed optical storage of the kind demonstrated in
photorefractive crystals and rare-earth-ion-doped media: many patterns share one physical
volume, separated by spectral channel, and content-addressed recall is a parallel optical
*correlation* (the readout beam reconstructs the closest stored pattern). Here that
correlation is simulated with hashed embeddings + cosine overlap, which is exactly the
operation an optical correlator performs in O(1) passes regardless of how many patterns
are multiplexed — the source of photonic associative-memory parallelism.

This is a physics-inspired simulation (it runs on a CPU), not a device driver. The point is
that it satisfies the *same* `Backend` interface as the classical reference.
"""
from __future__ import annotations

from .base import Backend, embed, cosine


class PhotonicHolographicBackend(Backend):
    name = "photonic"
    substrate = "spectral-spatial holography (photorefractive / REIC)"

    def __init__(self, channels: int = 256) -> None:
        self.channels = channels            # spectral multiplexing capacity
        self._store: dict[str, dict] = {}
        self._holo: dict[str, list[float]] = {}

    def write(self, address: str, pattern: dict) -> None:
        if len(self._store) >= self.channels:
            raise MemoryError(f"spectral capacity {self.channels} reached "
                              "(increase channels = wider optical bandwidth)")
        self._store[address] = pattern
        text = pattern.get("text") or pattern.get("summary") or str(pattern.get("value", ""))
        self._holo[address] = embed(text)

    def read(self, address: str) -> dict | None:
        return self._store.get(address)

    def query(self, cue: str, k: int = 1) -> list[tuple[str, float]]:
        # one parallel correlation against all multiplexed holograms (O(1) optical passes)
        probe = embed(cue)
        scored = sorted(((a, cosine(probe, h)) for a, h in self._holo.items()),
                        key=lambda x: x[1], reverse=True)
        return scored[:k]

    def reconstruct(self) -> dict:
        # the superposed wavefront: sum of all stored holograms = global structure
        dim = 64
        acc = [0.0] * dim
        for h in self._holo.values():
            for i, v in enumerate(h):
                acc[i] += v
        return {"multiplexed": len(self._store), "channels": self.channels,
                "superposed_energy": round(sum(a * a for a in acc), 4),
                "addresses": list(self._store.keys())}

    def stats(self) -> dict:
        return {"backend": self.name, "substrate": self.substrate,
                "multiplexed": len(self._store), "channels": self.channels,
                "recall": "parallel optical correlation (substrate-parallel)",
                "coherence": "ms–s (material dependent)"}
