"""Demo: generate a structured artifact while 'reading the whole book' from Mnestra,
then swap the substrate underneath without changing a line of generation logic.

Run:  python examples/demo_structured_generation.py
"""
from mnestra import MnestraMemory, Codex, Slot, MockLLM
from mnestra.backends import ClassicalBackend, PhotonicHolographicBackend, AFCBackend


def build_book() -> Codex:
    plan = [
        Slot("s0", "Thesis", constraints=["must define 'structure-complete memory'"],
             shared_facts=["holography_principle"]),
        Slot("s1", "Physics", deps=["s0"], shared_facts=["holography_principle", "afc_protocol"]),
        Slot("s2", "Logical model", deps=["s0", "s1"], shared_facts=["holography_principle"]),
        Slot("s3", "Efficiency", deps=["s2"], constraints=["must cite the benchmark speedup"]),
        Slot("s4", "Conclusion", deps=["s0", "s3"]),
    ]
    cons = [c for s in plan for c in s.constraints]
    for s in plan:
        s.constraints = cons  # the whole plan's constraints are known up front
    return Codex("Why structure-complete memory matters", plan)


def write_book(backend, label):
    codex = build_book()
    mem = MnestraMemory(backend, codex)
    llm = MockLLM()
    print(f"\n=== substrate: {label} ({mem.stats().get('substrate')}) ===")
    for slot in codex.plan:
        view = mem.read_whole_book(slot.id)            # the 'rest of the book'
        ctx = (f"constraints={view['constraints']} deps={list(view['dep_summaries'])} "
               f"recalled={[r['address'][:6] for r in view['recalled']]} :: {slot.title}")
        for f in slot.shared_facts:
            llm.derive_fact(f, memoized=True)          # derive-once shared facts
        out = llm.generate(ctx)
        mem.commit(slot.id, content=f"[{slot.title}] {out}", summary=f"sum:{slot.title}")
        print(f"  {slot.id} {slot.title:14} -> {out}  (recall {view['recalled'][0]['score']:.2f})")
    print(f"  LLM cost: {llm.snapshot()}")
    print(f"  reconstruct(): {mem.reconstruct()}")


if __name__ == "__main__":
    # identical generation loop, three substrates
    write_book(ClassicalBackend(), "classical")
    write_book(PhotonicHolographicBackend(channels=64), "photonic")
    write_book(AFCBackend(finesse=12, modes=32), "quantum")
