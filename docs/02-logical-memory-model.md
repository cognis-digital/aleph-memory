# 2. The logical memory model

The logical model is what application code and language bindings see. It is small on purpose —
five operations and one addressing rule — so that it can be honoured by a digital hash table, an
optical correlator, or an atomic frequency comb alike.

## 2.1 Content addressing

An address is the BLAKE2b-128 of the canonical encoding of a payload. Equal meaning → equal
address, on every substrate, in every language. Addresses are *semantic handles*, not memory
locations, which is what lets the same reference resolve whether the bytes live in RAM, in a
crystal's spectral channel, or in a comb mode.

## 2.2 The five operations

| Op | Meaning | Classical | Photonic | Quantum |
|----|---------|-----------|----------|---------|
| `write(addr, pattern)` | store a pattern at a content address | table insert | burn fringe set | program comb mode |
| `read(addr)` | exact (positional) recall | table lookup | addressed read-beam | timed echo |
| `query(cue, k)` | **associative** recall by meaning | ANN over embeddings | optical correlation | quantum-associative recall |
| `reconstruct()` | the structure-complete global view | aggregate summary | superposed wavefront | collective re-emission |
| `stats()` | substrate health | capacity | channels | finesse/fidelity/coherence |

`query` and `reconstruct` are the operations classical pointer-memory lacks and that make Mnestra
useful to a generator: *recall by meaning* and *recover the whole from a part*.

## 2.3 The Codex: structure-complete artifacts

On top of the store sits the **Codex** — the data model for "a book being written": a plan of
**slots**, each with dependencies, cross-slot **constraints**, and **shared facts**. Crucially the
*entire plan exists before any slot is filled*, and every slot's summary is content-addressed as
it is written. So at any step a generator can call `read_whole_book(slot)` and get a compact,
bounded view: the outline, the constraints in force, the summaries of the slots it depends on, and
a couple of associatively-recalled related regions — never the raw growing transcript.

This is the difference between *re-reading everything you have written so far* (causal, O(N²)) and
*recalling the few relevant parts plus the global skeleton* (Mnestra, ~O(N)). See
[doc 4](04-llm-read-the-whole-book.md) for the measured consequence.
