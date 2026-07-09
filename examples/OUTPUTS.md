# Captured outputs

Real output from running this repo (not hand-written). Reproduce with the commands shown.

## Efficiency benchmark — `python -m mnestra.bench`

```
slots=  10  causal_work=    4195  mnestra_work=    244  speedup= 17.19x  recompute_avoided=  30  retries_avoided=  5
slots=  40  causal_work=   92560  mnestra_work=   1204  speedup= 76.88x  recompute_avoided= 120  retries_avoided= 35
slots= 100  causal_work=  610030  mnestra_work=   4204  speedup=145.11x  recompute_avoided= 300  retries_avoided= 95
```

Speedup grows with artifact size — the signature of an O(N²)→O(N) change, not a constant factor.

## Substrate-swap demo — `python examples/demo_structured_generation.py`

The *same* generation loop runs on all three substrates. Note the generated content addresses
are **identical across substrates** (content addressing is substrate-independent), and the quantum
backend's recall scores are scaled by AFC retrieval efficiency (~0.52 at finesse 12).

```
=== substrate: classical (digital RAM / phase-change (GST)) ===
  s0 Thesis         -> <gen:3048ca7390>  (recall 0.33)
  s2 Logical model  -> <gen:151c5cd75b>  (recall 0.71)
  reconstruct(): {'records': 6, ...}

=== substrate: photonic (spectral-spatial holography (photorefractive / REIC)) ===
  s2 Logical model  -> <gen:151c5cd75b>  (recall 0.71)
  reconstruct(): {'multiplexed': 6, 'channels': 64, 'superposed_energy': 13.59, ...}

=== substrate: quantum (atomic frequency comb in rare-earth-ion-doped crystal) ===
  s2 Logical model  -> <gen:151c5cd75b>  (recall 0.37)
  reconstruct(): {'stored_modes': 6, 'finesse': 12, 'retrieval_efficiency': 0.5206,
                  'storage_time_s': 3600.0, ...}
```

## Tests — `pytest -q`

```
..........                                                               [100%]
10 passed
```
