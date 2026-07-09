# 3. Forward compatibility across substrates

"Forward-compatible" has a precise meaning here: **the same program, unchanged, runs on classical
hardware today and on photonic or quantum hardware as it matures.** This is achievable only
because the substrate is hidden behind the five-operation interface (doc 2). Swapping substrates
is a one-line change of backend.

```python
from mnestra import MnestraMemory, Codex
from mnestra.backends import ClassicalBackend, PhotonicHolographicBackend, AFCBackend

mem = MnestraMemory(ClassicalBackend(), codex)              # runs anywhere today
mem = MnestraMemory(PhotonicHolographicBackend(channels=256), codex)  # optical, when available
mem = MnestraMemory(AFCBackend(finesse=12, modes=64), codex)          # quantum, when available
```

Everything above the backend line — the Codex, `read_whole_book`, the language bindings — is
untouched.

## 3.1 What each backend is

- **`ClassicalBackend`** — the reference. Exact content-address table + hashed-embedding
  associative index. Maps to RAM now, phase-change (GST) non-volatile memory next. Fully runnable.
- **`PhotonicHolographicBackend`** — *simulation* of spectral-spatial holography: many patterns
  multiplexed in one volume, recalled by a single parallel correlation (an optical correlator does
  this in O(1) passes regardless of how many patterns are stored — the source of photonic
  associative-memory parallelism). Enforces a spectral capacity bound.
- **`AFCBackend`** — *simulation* of an atomic frequency comb in REIC: multimode temporal capacity,
  retrieval efficiency that rises and saturates with comb finesse, hour-class storage time. Recall
  is fidelity-weighted by efficiency.

The photonic and quantum backends are physics-inspired simulations that run on a CPU; they exist to
prove the interface is substrate-neutral and to let you develop against tomorrow's hardware today.
They are honestly labelled as simulations in their module docstrings — they are not device drivers.

## 3.2 The maturity ladder

| Stage | Substrate | Mnestra backend | Status |
|---|---|---|---|
| now | RAM / phase-change | `ClassicalBackend` | production-real |
| near | integrated photonic (PCM-on-waveguide) | `PhotonicHolographicBackend` | sim → driver |
| horizon | REIC quantum memory (AFC) | `AFCBackend` | sim → driver (cryogenic) |

Because the contract never changes, code and data written at one stage survive to the next.
