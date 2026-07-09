# 1. Scientific foundations

Mnestra rests on a single, lucky fact of materials physics: **one family of materials can store
information classically, photonically, and quantum-mechanically.** That is what makes a
genuinely *forward-compatible* memory possible — you are not betting on three unrelated
technologies converging, you are betting on three regimes of the *same* substrate.

## 1.1 The unifying substrate: rare-earth-ion-doped crystals (REIC)

Crystals lightly doped with rare-earth ions — most studied are **Eu³⁺:Y₂SiO₅**,
**Pr³⁺:Y₂SiO₅**, and **Er³⁺**-doped hosts (telecom band) — have extraordinarily narrow optical
and spin transitions because the optically active 4f electrons are shielded by outer shells
from electric and magnetic noise. The same shielding that buys long coherence is what lets the
material be driven through three storage regimes:

| Regime | Mechanism in REIC | What it stores |
|---|---|---|
| **Classical** | *Spectral hole burning* — burn persistent holes into the inhomogeneous absorption line; each frequency is a bit/symbol | dense frequency-multiplexed classical data |
| **Photonic** | *Spectral–spatial holography / photon echoes* — interference patterns across frequency and space, recalled by a rephasing pulse | analog optical patterns, many multiplexed at once |
| **Quantum** | *Atomic Frequency Comb (AFC)*, CRIB/GEM, EIT — collective absorption and timed re-emission preserving quantum state | single-photon and time-bin **qubit** states |

The logical operations of Mnestra (`write`, `read`, `query`, `reconstruct`) map onto each regime
without changing — only the physics underneath differs.

## 1.2 Why these numbers matter

Recent results show the regime is not science fiction:

- **1-hour coherent optical storage** was demonstrated in ¹⁵¹Eu³⁺:Y₂SiO₅ using a spin-wave AFC
  protocol in a zero-first-order-Zeeman (ZEFOZ) field.
- **~370-minute (6-hour-class) optical coherence** via dynamical decoupling at ~2 K.
- **30+ hour spin lifetimes** reported in 2025 for Eu³⁺:Y₂O₃ ceramics — a solid-state record —
  by isolating the ion's inner electrons from external noise.
- **AFC multimode storage**: a comb of periodic absorption peaks stores many *temporal modes* in
  parallel, the property that makes REIC attractive for quantum repeaters.

A memory that holds a quantum state for an hour, or a classical pattern indefinitely (with
refresh/ECC), in the *same* crystal, is the physical justification for a single logical model
that spans all three.

## 1.3 Near-term engineering bridge: phase-change & integrated photonics

REIC quantum memory needs cryogenics today. For the **classical** and **photonic** regimes that
run at room temperature, the practical substrate is **chalcogenide phase-change material**
(e.g. Ge–Sb–Te): non-volatile multilevel resistance states for classical storage, and
PCM-on-waveguide cells for **integrated photonic memory**, which already demonstrate in-memory
optical compute. Mnestra's classical and photonic backends target these now; the quantum (AFC)
backend targets REIC as cryogenic photonic memory matures. Same interface throughout.

## 1.4 The conceptual leap: holography ⇒ "read the whole book"

A hologram has a defining property: **every region encodes the whole.** Illuminate a fragment
and you reconstruct the entire scene (at reduced resolution). Spectral–spatial holography in
REIC is literally this, in frequency–space. Mnestra lifts that property to the *logical* layer:
information is stored so that the **global structure is recoverable from any address**. A reader
positioned anywhere can recover "the rest of the book" — which is exactly the access pattern a
language model needs to stop re-deriving context (see [doc 4](04-llm-read-the-whole-book.md)).

> Sources for the physics claims are linked from the README's "References" section. This document
> synthesizes published results; it does not reproduce them.
