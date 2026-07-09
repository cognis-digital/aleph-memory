"""Benchmark: why "reading the whole book" is cheaper.

Two strategies generate the SAME structured artifact (a Codex of N slots that share derived
facts and carry cross-slot constraints):

  causal  — the status quo. Generate left-to-right; each step attends over the growing raw
            transcript; shared facts are re-derived at every use; constraints that surface
            late force regeneration (retries). Cost ~ O(N^2) context + redundant derivations
            + retries.

  mnestra   — content-address only the *relevant* prior slots (a few dependency summaries) plus
            the global constraints, all known up front from the plan. Shared facts are derived
            once and memoized. Cost ~ O(N) context, zero re-derivation, zero constraint retries.

Numbers below are produced by running the actual MockLLM cost model — nothing is hard-coded.
The MockLLM is a cost model, not a transformer; `work_tokens` (context processed) is the
proxy for compute/latency, since attention cost scales with context length.
"""
from __future__ import annotations

import json

from .codex import Codex, Slot
from .llm import MockLLM
from .model import MnestraMemory
from .backends import ClassicalBackend

SLOT_WORDS = 40          # raw content size carried in a causal transcript
SUMMARY_WORDS = 6        # compact summary size carried in an Mnestra view


def make_codex(n_slots: int = 40, n_facts: int = 8) -> Codex:
    facts = [f"sharedfact{i}" for i in range(n_facts)]
    plan: list[Slot] = []
    for i in range(n_slots):
        deps = [f"s{j}" for j in {max(0, i - 1), i // 2} if j < i]
        used = [facts[(i + k) % n_facts] for k in range(3)]   # reuses facts across slots
        # every 5th slot imposes a global constraint that earlier slots must respect
        constraints = [f"constraint_from_s{i}"] if i % 5 == 0 else []
        plan.append(Slot(id=f"s{i}", title=f"section {i}", deps=deps,
                         constraints=constraints, shared_facts=used))
    # propagate each late constraint onto all earlier slots (the source of causal retries)
    cons = [f"constraint_from_s{i}" for i in range(n_slots) if i % 5 == 0]
    for s in plan:
        s.constraints = list(cons)
    return Codex("Benchmark Compendium", plan)


def _content(slot: Slot) -> str:
    return f"{slot.title} " + " ".join([f"w{k}" for k in range(SLOT_WORDS)])


def run_causal(codex: Codex) -> dict:
    llm = MockLLM()
    transcript: list[str] = []
    retries = 0
    for slot in codex.plan:
        context = " ".join(transcript) + f" PROMPT {slot.title}"
        for f in slot.shared_facts:
            llm.derive_fact(f, memoized=False)          # re-derive every use
        llm.generate(context)
        transcript.append(_content(slot))
    # constraints are only reconciled after the fact: every slot that predates a constraint
    # source must be regenerated once against the (now full) transcript.
    full = " ".join(transcript)
    for slot in codex.plan:
        late = [c for c in slot.constraints if int(c.split("s")[-1]) > int(slot.id[1:])]
        if late:
            retries += 1
            llm.generate(full + f" REPAIR {slot.title} for {late}")
    snap = llm.snapshot(); snap["retries"] = retries; snap["strategy"] = "causal"
    return snap


def run_mnestra(codex: Codex) -> dict:
    llm = MockLLM()
    mem = MnestraMemory(ClassicalBackend(), codex)
    for slot in codex.plan:
        view = mem.read_whole_book(slot.id)             # compact, content-addressed
        ctx = (f"CONSTRAINTS {' '.join(view['constraints'])} "
               + " ".join((codex.slot(d).summary or d) + " "
                          + " ".join(f"u{k}" for k in range(SUMMARY_WORDS))
                          for d in codex.slot(slot.id).deps)
               + f" PROMPT {slot.title}")
        for f in slot.shared_facts:
            llm.derive_fact(f, memoized=True)           # derive once, reuse forever
        llm.generate(ctx)
        mem.commit(slot.id, _content(slot), summary=f"sum {slot.title}")
    # constraints were known from the plan up front → no repair passes
    snap = llm.snapshot(); snap["retries"] = 0; snap["strategy"] = "mnestra"
    return snap


def benchmark(n_slots: int = 40, n_facts: int = 8) -> dict:
    codex = make_codex(n_slots, n_facts)
    causal = run_causal(make_codex(n_slots, n_facts))
    mnestra = run_mnestra(make_codex(n_slots, n_facts))
    speedup = round(causal["work_tokens"] / max(1, mnestra["work_tokens"]), 2)
    return {"params": {"slots": n_slots, "shared_facts": n_facts},
            "causal": causal, "mnestra": mnestra,
            "work_speedup_x": speedup,
            "recomputes_avoided": causal["recomputes"] - mnestra["recomputes"],
            "retries_avoided": causal["retries"] - mnestra["retries"]}


def main() -> None:
    print("Mnestra efficiency benchmark — causal vs. structure-complete memory\n")
    for n in (10, 40, 100):
        r = benchmark(n_slots=n)
        print(f"slots={n:>4}  causal_work={r['causal']['work_tokens']:>8}  "
              f"mnestra_work={r['mnestra']['work_tokens']:>7}  "
              f"speedup={r['work_speedup_x']:>6}x  "
              f"recompute_avoided={r['recomputes_avoided']:>4}  "
              f"retries_avoided={r['retries_avoided']:>3}")
    print("\nfull record (slots=40):")
    print(json.dumps(benchmark(40), indent=2))


if __name__ == "__main__":
    main()
