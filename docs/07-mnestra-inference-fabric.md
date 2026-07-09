# 7. The Mnestra Inference Fabric — composing the industrial stack

The Mnestra Inference Fabric (AIF) is a new memory **model** built by being *additive to* the best,
most-popular industrial techniques rather than replacing them. Each proven technique becomes a
**tier** over one content-addressed, substrate-agnostic store, so they share storage, dedup
against one another, and inherit Mnestra's forward-compatibility (classical → photonic → quantum).

Today these techniques are separate, ad-hoc memories with their own formats and lifetimes. AIF's
contribution is the *unification*: one address space (BLAKE2b content addresses), one backend
interface, one tiering/eviction policy.

## The tiers (and what each builds on)

| Tier | Proven industrial concept | What AIF adds |
|---|---|---|
| **L0 — KV pages** | **PagedAttention / vLLM** | pages keyed by *content* → identical pages (shared system prompts, repeated tool templates) stored once, deduped **globally**, not per-sequence |
| **L1 — prefix cache** | **prompt caching** (Anthropic, vLLM automatic prefix caching) | prefix addressing is just content addressing — same mechanism, same space as everything else |
| **L2 — working set** | *(novel)* **Mnestra Codex "whole-book"** | bounded, structure-complete global view instead of the raw transcript |
| **L3 — long-term** | **RAG over ANN** (FAISS / HNSW) | associative recall on the *same* store the caches live in |
| **router** | **MoE-style routing** | serve each request from the cheapest competent tier |
| **integrity / dedup** | **Merkle DAG / IPFS** content addressing | dedup + tamper-evidence for free |
| **persistence** | **LSM-tree tiering** | promote/evict across substrates: RAM → phase-change → photonic → quantum |

## Measured behavior (real cache metrics, not modeled speedups)

`python -m mnestra.fabric` runs a realistic workload — 40 requests sharing a 48-token system
prompt, with repeated bodies (tool templates / retries) and periodic retrievals. Computed from
the run:

```
prefix_hit_rate   : 0.975          # 39/40 requests reuse the shared prompt's compute
kv_pages_logical  : 200
kv_pages_physical : 81
kv_dedup_ratio    : 2.469          # identical KV pages collapse 2.5x
tiers_served      : prefix_cache 39, kv_dedup 1, retrieval 8, generate 0
```

Every request was served from a tier; none fell through to cold generation. These are genuine
cache/dedup numbers — the kind of metric that actually governs production cost — and they are the
**right** thing to measure, unlike the single-call prompt-length test in
[VALIDATION.md](../VALIDATION.md), which (honestly) showed ~1.0× because it cannot see cross-request
KV reuse.

## Why "additive" is the point

Nothing here asks you to abandon vLLM, your prompt cache, or your vector DB. AIF says: *put them
on one content-addressed substrate.* Then a prefix cached for request A is the same object a KV
page in request B dedups against, is the same record RAG retrieves later, addressed identically —
and the whole hierarchy is portable to photonic/quantum hardware without touching application code.

## Honesty

The dedup/hit numbers above are real and reproducible. The *LLM* wall-clock win from this sharing
is **not yet demonstrated end-to-end** — confirming it needs a served stack with automatic prefix
caching instrumented for KV-block reuse (see VALIDATION.md "what would actually confirm"). AIF is
the architecture that makes that measurement possible; the measurement itself is open work.
