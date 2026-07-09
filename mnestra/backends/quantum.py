"""Quantum backend — atomic-frequency-comb (AFC) memory (simulation).

Models the protocol that gives rare-earth-ion-doped crystals (e.g. 151-Eu3+:Y2SiO5,
Pr3+:Y2SiO5, Er3+ for telecom) their standing as leading solid-state quantum memories:
an absorption line is shaped into a comb of `finesse` periodic peaks with tooth spacing
Delta; an input photon is absorbed collectively and re-emitted as a photon echo after
time 1/Delta. The comb stores many *temporal modes* in parallel — the property that makes
AFC attractive for quantum repeaters. Demonstrated milestones this simulation is calibrated
against: 1-hour coherent storage and ~6-hour spin coherence in Eu:YSO.

This is a physics-inspired simulation, not control software for a dilution refrigerator.
It honours the *same* `Backend` interface, so logical Mnestra programs are already
forward-compatible with quantum hardware: only the substrate swaps.
"""
from __future__ import annotations

import math

from .base import Backend, embed, cosine


class AFCBackend(Backend):
    name = "quantum-afc"
    substrate = "atomic frequency comb in rare-earth-ion-doped crystal"

    def __init__(self, finesse: int = 10, modes: int = 64,
                 storage_time_s: float = 3600.0) -> None:
        self.finesse = finesse              # comb finesse → retrieval efficiency
        self.modes = modes                  # multimode temporal capacity
        self.storage_time_s = storage_time_s
        self._store: dict[str, dict] = {}
        self._spec: dict[str, list[float]] = {}

    def efficiency(self) -> float:
        # AFC retrieval efficiency rises then saturates with comb finesse (~tanh model,
        # bounded well under the no-cavity ceiling). Illustrative, not a fit.
        return round(0.54 * math.tanh(self.finesse / 6.0), 4)

    def write(self, address: str, pattern: dict) -> None:
        if len(self._store) >= self.modes:
            raise MemoryError(f"AFC multimode capacity {self.modes} reached")
        self._store[address] = pattern
        text = pattern.get("text") or pattern.get("summary") or str(pattern.get("value", ""))
        self._spec[address] = embed(text)

    def read(self, address: str) -> dict | None:
        rec = self._store.get(address)
        if rec is None:
            return None
        return {**rec, "_retrieval_efficiency": self.efficiency()}

    def query(self, cue: str, k: int = 1) -> list[tuple[str, float]]:
        # quantum-associative recall, fidelity-weighted by retrieval efficiency
        probe = embed(cue)
        eff = self.efficiency()
        scored = sorted(((a, cosine(probe, s) * eff) for a, s in self._spec.items()),
                        key=lambda x: x[1], reverse=True)
        return scored[:k]

    def reconstruct(self) -> dict:
        return {"stored_modes": len(self._store), "capacity_modes": self.modes,
                "finesse": self.finesse, "retrieval_efficiency": self.efficiency(),
                "storage_time_s": self.storage_time_s,
                "addresses": list(self._store.keys())}

    def stats(self) -> dict:
        return {"backend": self.name, "substrate": self.substrate,
                "finesse": self.finesse, "modes": f"{len(self._store)}/{self.modes}",
                "retrieval_efficiency": self.efficiency(),
                "coherence": f"~{self.storage_time_s/3600:.1f} h (Eu:YSO class)"}
