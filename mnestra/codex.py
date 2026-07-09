"""The Codex — "the book" an LLM is writing.

A Codex is a structure-complete representation of an artifact: a plan of slots, each with
dependencies, cross-references, and constraints, plus whatever content has been filled in.
Unlike a linear transcript, the *whole* structure is addressable at every step — so a
generator can "read the rest of the book" (the plan, sibling summaries, and not-yet-written
constraints) while writing any single slot. This is the data model that the Mnestra memory
makes cheap to hold and query on any substrate.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Slot:
    id: str
    title: str
    deps: list[str] = field(default_factory=list)          # slot ids this one references
    constraints: list[str] = field(default_factory=list)   # global facts it must respect
    shared_facts: list[str] = field(default_factory=list)  # derivations reused across slots
    content: str | None = None
    summary: str | None = None

    @property
    def filled(self) -> bool:
        return self.content is not None


class Codex:
    def __init__(self, title: str, plan: list[Slot]):
        self.title = title
        self.plan = plan
        self._by_id = {s.id: s for s in plan}

    def __len__(self) -> int:
        return len(self.plan)

    def slot(self, sid: str) -> Slot:
        return self._by_id[sid]

    def global_view(self, at: str) -> dict:
        """The 'rest of the book' relevant to slot `at`: the full outline, summaries of
        already-filled slots, the constraints that apply, and the dependency context.
        Bounded in size — this is the compact global hologram, not the raw transcript."""
        cur = self._by_id[at]
        return {
            "title": self.title,
            "outline": [f"{s.id}:{s.title}" for s in self.plan],
            "constraints": sorted(set(cur.constraints)),
            "dep_summaries": {d: (self._by_id[d].summary or "(unwritten)") for d in cur.deps},
            "filled": sum(1 for s in self.plan if s.filled),
            "total": len(self.plan),
        }

    def all_constraints(self) -> list[str]:
        seen: list[str] = []
        for s in self.plan:
            for c in s.constraints:
                if c not in seen:
                    seen.append(c)
        return seen
