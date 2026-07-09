"""MnestraMemory — the logical memory model, independent of substrate.

Wraps any `Backend` and a `Codex`, exposing the operations a generator uses to "read the
whole book": commit a slot, recall by meaning, and reconstruct the global structure-complete
view from any point. Swap the backend (classical / photonic / quantum) and nothing above
this line changes — that is the forward-compatibility guarantee.
"""
from __future__ import annotations

from .backends.base import Backend, content_address
from .codex import Codex, Slot


class MnestraMemory:
    def __init__(self, backend: Backend, codex: Codex):
        self.backend = backend
        self.codex = codex
        # the plan itself is written as the root hologram, readable from anywhere
        self.backend.write(content_address(("plan", codex.title)),
                           {"summary": f"plan:{codex.title}",
                            "text": " ".join(s.title for s in codex.plan)})

    def commit(self, sid: str, content: str, summary: str) -> str:
        slot = self.codex.slot(sid)
        slot.content, slot.summary = content, summary
        addr = content_address(("slot", sid, summary))
        self.backend.write(addr, {"slot": sid, "summary": summary, "text": content})
        return addr

    def read_whole_book(self, at: str) -> dict:
        """Compact global view for slot `at` (the structure-complete hologram), plus a
        couple of associatively-recalled related regions from the substrate."""
        view = self.codex.global_view(at)
        cue = self.codex.slot(at).title
        related = self.backend.query(cue, k=2)
        view["recalled"] = [{"address": a, "score": round(s, 3)} for a, s in related]
        return view

    def reconstruct(self) -> dict:
        return self.backend.reconstruct()

    def stats(self) -> dict:
        return self.backend.stats()
