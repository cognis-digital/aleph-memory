# Mnestra — a structure-complete memory fabric

**Read the whole book from any address. One logical memory, forward-compatible across classical,
photonic, and quantum hardware.**

Today a language model generates *causally* — left to right — re-attending over an ever-growing
transcript and re-deriving what it already knows. Mnestra is a memory model in which the **entire
structure of an artifact is recoverable from any single point** (the defining property of a
hologram), so a generator can *read the rest of the book* instead of recomputing it. In the
reference benchmark that turns an **O(N²)** access pattern into **O(N)** — a speedup that **grows
with size**: 17× at 10 sections, 77× at 40, **145× at 100**.

The same logical model runs on a hash table today and on a rare-earth quantum-memory crystal
tomorrow, because the substrate is hidden behind a five-operation interface.

```python
from mnestra import MnestraMemory, Codex, Slot
from mnestra.backends import ClassicalBackend, PhotonicHolographicBackend, AFCBackend

mem = MnestraMemory(ClassicalBackend(), codex)        # runs today
# mem = MnestraMemory(PhotonicHolographicBackend())   # optical, when available
# mem = MnestraMemory(AFCBackend(finesse=12))         # quantum, when available — same code

view = mem.read_whole_book("section_7")   # outline + constraints + recalled context, not the raw transcript
```

## The one idea

A **hologram**: every fragment encodes the whole. Spectral–spatial holography in rare-earth
crystals is literally this, in frequency–space. Mnestra lifts it to the logical layer: store
information so the **global structure is recoverable from any address**. That is exactly the access
pattern an LLM needs to stop re-deriving context.

## Why it can span quantum + photonic + classical

Because **one material family does all three.** Rare-earth-ion-doped crystals (Eu³⁺:Y₂SiO₅,
Pr³⁺:Y₂SiO₅, Er³⁺ hosts) store information:

| Regime | Mechanism | Demonstrated |
|---|---|---|
| **classical** | spectral hole burning (frequency-multiplexed bits) | decades of optical data storage |
| **photonic** | spectral–spatial holography / photon echoes | many patterns multiplexed in one volume |
| **quantum** | atomic frequency comb (AFC), EIT, CRIB/GEM | **1-hour** optical storage; ~370-min coherence; 30+ h spin lifetime (2025) |

So "forward-compatible across substrates" isn't a bet on three technologies converging — it's three
regimes of the *same* crystal. Room-temperature engineering uses phase-change (Ge–Sb–Te) and
integrated photonics now; REIC is the quantum horizon. Full detail:
[docs/01-scientific-foundations.md](docs/01-scientific-foundations.md).

## The efficiency, measured

`python -m mnestra.bench` (numbers produced by the run, not hard-coded):

| slots | causal work | mnestra work | speedup | recompute avoided | retries avoided |
|------:|------------:|-----------:|--------:|------------------:|----------------:|
| 10    | 4,195       | 244        | **17.2×** | 30 | 5 |
| 40    | 92,560      | 1,204      | **76.9×** | 120 | 35 |
| 100   | 610,030     | 4,204      | **145.1×** | 300 | 95 |

Three savings, all real: bounded global view instead of a growing transcript (O(N²)→O(N)),
derive-once content-addressed shared facts, and zero constraint backtracking because the whole plan
is known up front. The benchmark's LLM is a faithful **cost model**, not a transformer — see
[docs/04](docs/04-llm-read-the-whole-book.md) for exactly what is and isn't claimed.

## A new model, additive to the industrial stack

The **Mnestra Inference Fabric** ([docs/07](docs/07-mnestra-inference-fabric.md)) doesn't replace the
proven techniques — it **composes** them on one content-addressed substrate. Each is a tier:
PagedAttention/vLLM (KV pages), prompt caching (prefix), RAG over HNSW/FAISS (long-term),
MoE-style routing, Merkle/IPFS dedup, LSM tiering — plus Mnestra's novel "whole-book" working set.
Run it: `python -m mnestra.fabric` → on a realistic workload it measures **97.5% prefix-hit** and
**2.47× KV-page dedup**, every request served from a tier (real cache metrics, computed from the run).

## Real-model validation — honest

Two honest measurements on live models:
- A **single-call** test (OmniCoder-9B via Ollama) measured **~1.0×** — because independent-call
  token counting *cannot see* cross-request KV reuse, which is where the savings live.
- The **served-stack** test (`python -m mnestra.kv_harness`, llama.cpp `:8774`) measured it correctly:
  content-addressed prefix reuse cut **prompt-eval time 58×** and **wall-clock 14×** on a
  prefix-sharing workload. The token *count* is unchanged (the tell that misled the single-call
  test); the *compute* collapses because the shared prefix's KV isn't recomputed.

So: the serving-layer win is **real and measured**; the `mnestra.bench` 17–145× figures remain
labelled as cost-model access-pattern properties, not transformer wall-clock. Full write-up,
diagnosis, and scope in [VALIDATION.md](VALIDATION.md).

## Architecture

```
        application / any language  ──────────────┐
                                                   │  spec/mnestra.idl  (5 ops + 1 address rule)
        ┌──────────────────────────────────────────┘
        │   MnestraMemory  ·  Codex ("the book")  ·  read_whole_book()
        │
        │   Backend interface:  write · read · query · reconstruct · stats
        ├── ClassicalBackend            RAM / phase-change      (runs — reference)
        ├── PhotonicHolographicBackend  spectral-spatial optics (simulation)
        └── AFCBackend                  rare-earth quantum AFC  (simulation)
```

Content addressing (BLAKE2b-128 of canonical payload) is the bridge: equal meaning → equal address,
on every substrate, in every language.

## Quickstart

```bash
git clone https://github.com/cognis-digital/mnestra && cd mnestra
python -m mnestra.bench                              # the efficiency benchmark
python examples/demo_structured_generation.py      # same loop, 3 substrates
pip install -e ".[dev]" && pytest -q               # 10 tests
```

Pure standard library — no dependencies — so it runs anywhere.

## Repo map

- [`mnestra/`](mnestra) — runnable reference (model, codex, llm cost-model, 3 backends, benchmark)
- [`docs/`](docs) — the whitepaper: [foundations](docs/01-scientific-foundations.md) ·
  [logical model](docs/02-logical-memory-model.md) ·
  [forward compatibility](docs/03-forward-compatibility.md) ·
  [read the whole book](docs/04-llm-read-the-whole-book.md) ·
  [spec & bindings](docs/05-portable-spec-and-bindings.md) ·
  [roadmap & open problems](docs/06-roadmap-open-problems.md) ·
  [inference fabric](docs/07-mnestra-inference-fabric.md) · [glossary](docs/glossary.md)
- [`VALIDATION.md`](VALIDATION.md) — honest real-model validation (and why it measured ~1.0×)
- [`spec/`](spec) — language-neutral interface + container format
- [`bindings/`](bindings) — C ABI + Rust/Go/TypeScript surfaces (one interface, every language)

## What's real vs. forward-looking

The classical backend, the Codex access model, the benchmark, and the tests **run today**. The
photonic and quantum backends are honestly-labelled physics-inspired **simulations** that prove the
interface is substrate-neutral and let you build against future hardware now. No speedup in this
repo is asserted without `python -m mnestra.bench` reproducing it. The hard open problems are in
[docs/06](docs/06-roadmap-open-problems.md).

## References (physics)

- One-hour coherent optical storage in an AFC memory (Eu³⁺:Y₂SiO₅) — *Nature Communications* (2021).
- Long optical coherence via dynamical decoupling in Eu³⁺:Y₂SiO₅ (~6 h class).
- Long spin lifetimes in Eu³⁺:Y₂O₃ ceramics for quantum memories — *Communications Physics* (2025).
- Time-bin qubit storage in rare-earth crystals — *npj Quantum Information* (2022).

*This README synthesizes published results; it does not reproduce them.*

## License

COCL (Cognis Open Collaboration License) © Cognis Digital.
