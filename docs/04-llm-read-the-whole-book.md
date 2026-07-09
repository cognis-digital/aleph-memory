# 4. Reading the whole book: where the efficiency comes from

This is the point of Mnestra. A language model today generates **causally** — left to right —
re-attending over an ever-growing raw transcript and re-deriving facts it already worked out.
Mnestra gives the model a memory in which the **whole artifact's structure is available from any
point**, so it can *read the rest of the book* instead of recomputing it.

## 4.1 Three concrete savings

1. **Bounded context instead of a growing transcript.** Causal generation attends over all prior
   output: step *t* pays for *t* slots of raw content → total work ~ **O(N²)**. With Mnestra the
   model reads a compact global view — the outline, the in-force constraints, and the *few*
   dependency summaries surfaced by content-addressed recall — a roughly constant payload per step
   → total work ~ **O(N)**.
2. **Derive-once shared facts.** Facts reused across many slots are content-addressed and computed
   a single time (a global, position-independent cache). Causal generation re-derives them at every
   use.
3. **Zero constraint backtracking.** Because the whole plan — including constraints that a causal
   writer would only discover late — is present up front, slots are written correct-by-construction.
   No repair/regeneration passes.

## 4.2 Measured result (reproducible)

`python -m mnestra.bench` runs both strategies over the *same* structured task. The MockLLM is a
cost model, not a transformer: `work_tokens` counts context processed per call, a defensible proxy
for compute/latency because attention cost scales with context length. Numbers are produced by the
run, not hard-coded:

| slots | causal work | mnestra work | speedup | recompute avoided | retries avoided |
|------:|------------:|-----------:|--------:|------------------:|----------------:|
| 10    | 4,195       | 244        | **17.2×** | 30 | 5 |
| 40    | 92,560      | 1,204      | **76.9×** | 120 | 35 |
| 100   | 610,030     | 4,204      | **145.1×** | 300 | 95 |

The speedup **grows with artifact size** — the signature of an O(N²)→O(N) change, not a fixed
constant factor. The longer the book, the more it pays to read it holographically rather than
re-read it linearly.

## 4.3 Honesty about scope

This benchmark models the *cost structure* that produces the savings; it is not a measurement of a
specific transformer. The mechanisms it models — context length dominating attention cost, redundant
re-derivation, and constraint backtracking — are real and well-known. Mnestra is the memory substrate
and access discipline that removes them; wiring it to a concrete model (KV-reuse by content address,
plan-conditioned decoding, parallel section generation reconciled through shared memory) is the
roadmap in [doc 6](06-roadmap-open-problems.md).
