# 6. Roadmap & open problems

Mnestra is a coherent model with a runnable classical reference and honestly-simulated photonic and
quantum backends. The hard, interesting work is turning the simulations into drivers and wiring the
memory to a real model. Stated plainly so contributors know what is real and what is open.

## Real today
- Substrate-agnostic interface + content addressing.
- Classical backend (RAM/PCM-targetable), runnable.
- Codex / `read_whole_book` structure-complete access.
- Reproducible efficiency benchmark (O(N²)→O(N) separation).

## Near-term engineering
- **Photonic driver.** Replace the holography *simulation* with a PCM-on-waveguide or
  photorefractive correlator driver; validate that recall is one optical pass independent of N.
- **Real-model integration.** Bind `read_whole_book` to an actual LLM: (a) content-addressed KV
  reuse, (b) plan-conditioned/lookahead decoding, (c) parallel section generation reconciled through
  shared Mnestra memory. Measure wall-clock and token savings on a real transformer to confirm the
  modeled speedups.
- **Embeddings.** Swap the hashed bag-of-words for a learned embedding behind the same `embed`
  seam; everything else is unchanged.

## Open research
- **Quantum-associative recall.** Is there a useful, NISQ-feasible associative `query` on an AFC
  memory (Grover-style amplitude amplification over stored modes), and what fidelity does it need?
- **Error model.** Map ECC/refresh (classical), fringe decay (photonic), and decoherence/efficiency
  (quantum) into one logical reliability contract so `stats()` means the same thing everywhere.
- **Capacity vs. coherence vs. multiplexing** trade curves per substrate, exposed as a planner that
  picks a backend for a workload.
- **Security.** Content addresses leak equality; when is that acceptable, and what is the private
  variant?

## Non-goals
- Not a vector database (though it can use one as the classical associative index).
- Not a claim that quantum memory is production-ready — it is the *forward* in forward-compatible.
- No hype: every speedup in this repo is reproduced by `python -m mnestra.bench`.
