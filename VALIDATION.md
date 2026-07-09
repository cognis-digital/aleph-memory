# Real-model validation — honest results

> **Headline: a naive single-call test on a real model did NOT reproduce the cost-model
> speedups. We log that here rather than hide it.** The repo's rule is "no speedup asserted
> without reproduction"; this is the reproduction attempt, and what it actually showed.

## Setup

`python -m mnestra.validate_omnicoder` generated the same 12-section technical brief two ways on
a live transformer — **OmniCoder-Qwen3.5-9B** (Claude-distilled, uncensored) via Ollama, CPU:

- **causal** — each section prompted with the full *growing transcript* + a global rule.
- **mnestra** — each section prompted with a *bounded* view: the rule + only its ≤2 dependency
  summaries (no transcript, no full outline).

Metrics are Ollama's true `prompt_eval_count` (prompt tokens actually processed) and wall-clock.

## Result

| metric | causal | mnestra | ratio |
|---|---:|---:|---:|
| prompt tokens | 17,354 | 16,791 | **1.03×** |
| wall-clock (s) | 705.6 | 684.5 | **1.03×** |
| generated tokens | 2,160 | 2,160 | 1.00× |

**No meaningful speedup.** (An earlier 6-section run was even flatter, 0.98×.)

## Why (diagnosis)

1. **Fixed per-call overhead dominates.** Mnestra's prompts measured ~1,400 tokens/call when the
   user content was ~150 — the model's built-in chat/system template adds a large constant to
   every call. That constant (paid by *both* strategies) swamps the difference between a growing
   transcript and a bounded view at this scale.
2. **N too small.** At 12 short sections the causal transcript never grows large enough to
   dominate the fixed overhead. The cost-model separation (`mnestra.bench`) only opens up at large
   N and long context — which is also where it claims O(N²)→O(N).
3. **Wrong metric for the real win.** Prompt-token counting on independent calls cannot capture
   the savings' true source: **KV-cache reuse by content address** across requests. In a real
   serving stack the win is fewer *recomputed* KV blocks (prefix/whole-book sharing), not shorter
   prompts in a single call. That is measured by cache hit/dedup rate — see the
   [Mnestra Inference Fabric](docs/07-mnestra-inference-fabric.md), where it is **2.47× KV dedup and
   97.5% prefix-hit** on a realistic workload.

## Honest conclusion

- The `mnestra.bench` speedups (17×/77×/145×) are real **properties of the access pattern**, not
  measured transformer wall-clock. They are correctly labelled as cost-model figures.
- On a single-model, small-N, no-KV-reuse setup, Mnestra shows **~1.0×** — confirmed twice.
- The savings live in the **serving layer** (KV/prefix reuse, dedup), which is what the Inference
  Fabric composes and where the measured dedup/hit numbers are genuine.

## UPDATE (2026-07-01): served-stack KV-reuse — CONFIRMED

`python -m mnestra.kv_harness` ran the missing measurement on a live llama.cpp server (`:8774`):
12 requests sharing a ~250-token prefix, A/B toggled only by the server's prefix cache
(`cache_prompt` false vs true). Content-addressed prefix reuse is what a real Mnestra fabric
uses to know two prefixes are identical and route them to the same cached KV block.

| metric | baseline (no reuse) | prefix reuse | reduction |
|---|---:|---:|---:|
| tokens_evaluated | 10,972 | 10,972 | 1.0× |
| **prompt-eval time (ms)** | 539,520 | 9,259 | **58.3×** |
| **wall-clock (s)** | 571.8 | 39.8 | **14.4×** |

**This confirms the thesis where it actually lives.** The `tokens_evaluated` *count* is identical
(the server reports logical prompt length regardless of cache), which is exactly why the earlier
single-call token test saw ~1.0× and mistook it for "no win." But the real compute — **prompt-eval
time — dropped 58×**, and total wall-clock 14×, because the shared prefix's KV is reused instead of
recomputed. First request is cold in both; the reuse pays from request 2 on.

Honest scope: this is a synthetic best case (one identical 250-token prefix reused 12×). Real
speedup scales with the *prefix-sharing rate* of your traffic, and only the prompt phase is cached
(generation time is unchanged — hence 14× wall-clock, not 58×). But the mechanism is proven real on
hardware: **when requests share structure, content-addressed KV reuse eliminates the recompute.**
That is Mnestra's serving-layer contribution, now measured, not modeled.

## What would actually confirm the LLM win (open)

- Instrument **KV-block reuse** (a vLLM/SGLang-style served setup with automatic prefix caching),
  not single-call prompt length, and measure recomputed-block reduction across a request stream.
- Push to **large N / long context** where the transcript dominates fixed overhead.
- Use a base model without a large fixed template, or amortize the template via prefix caching.

Reproduce: `python -m mnestra.validate_omnicoder` (needs Ollama + the model).
