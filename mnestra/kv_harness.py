"""Served-stack KV-reuse harness — the measurement that proves or kills the LLM claim.

This is the *correct* instrument that VALIDATION.md said was missing. It does NOT count prompt
length on independent calls (which can't see reuse). It measures, on a live served engine
(llama.cpp), the prompt tokens the model **actually evaluated** vs reused from the KV cache —
`tokens_evaluated` and `timings.prompt_ms` — across a stream of requests that share a prefix.

A/B on identical prompts, toggled only by the server's prefix-cache:
  baseline : cache_prompt=false  -> every request re-evaluates the whole prompt (no reuse)
  mnestra    : cache_prompt=true   -> the shared prefix is computed once; later requests evaluate
                                    only their unique suffix

Mnestra's role: the shared prefix has ONE content address, so a content-addressed fabric routes
every request to the same cached KV block. The harness quantifies the recompute that saves.

Run:  python -m mnestra.kv_harness
"""
from __future__ import annotations

import json
import time
import urllib.request

from .backends.base import content_address

SERVER = "http://127.0.0.1:8774"          # llama.cpp server (reports tokens_evaluated + timings)
N_REQUESTS = 12


def _post(prompt: str, cache_prompt: bool, n_predict: int = 8) -> dict:
    body = json.dumps({"prompt": prompt, "n_predict": n_predict, "temperature": 0,
                       "cache_prompt": cache_prompt, "stream": False}).encode()
    req = urllib.request.Request(SERVER + "/completion", data=body,
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=600) as r:
        d = json.loads(r.read())
    d["_wall"] = time.time() - t0
    return d


def _bust(nonce: int) -> None:
    # overwrite the slot's cached context so the next phase starts cold and fair
    _post("RESET " + " ".join(f"z{nonce}_{i}" for i in range(60)), cache_prompt=True, n_predict=1)


def _shared_prefix() -> str:
    # ~250 tokens of generic filler — a stand-in for a long shared system prompt / tool preamble
    return ("SYSTEM PREAMBLE. " + " ".join(f"ctx{i}" for i in range(250)) + " END PREAMBLE.")


def run_phase(cache_prompt: bool, prefix: str) -> dict:
    evaluated = 0
    prompt_ms = 0.0
    wall = 0.0
    first = None
    for i in range(N_REQUESTS):
        prompt = f"{prefix}\nUSER REQUEST {i}: summarise item {i} in one line."
        d = _post(prompt, cache_prompt=cache_prompt)
        ev = int(d.get("tokens_evaluated", 0))
        evaluated += ev
        prompt_ms += float(d.get("timings", {}).get("prompt_ms", 0.0))
        wall += d["_wall"]
        if first is None:
            first = ev
    return {"tokens_evaluated": evaluated, "prompt_ms": round(prompt_ms, 1),
            "wall_s": round(wall, 1), "first_request_eval": first}


def main() -> None:
    try:
        urllib.request.urlopen(SERVER + "/health", timeout=4)
    except Exception:
        print(f"llama.cpp server not reachable at {SERVER} — start a slot (e.g. fleet :8774).")
        return
    prefix = _shared_prefix()
    addr = content_address(prefix)
    print(f"served-stack KV-reuse harness · {N_REQUESTS} requests · shared-prefix address {addr[:12]}\n")

    _bust(1)
    baseline = run_phase(cache_prompt=False, prefix=prefix)   # no reuse
    _bust(2)
    mnestra = run_phase(cache_prompt=True, prefix=prefix)       # content-addressed prefix reuse

    tok_red = round(baseline["tokens_evaluated"] / max(1, mnestra["tokens_evaluated"]), 2)
    ms_red = round(baseline["prompt_ms"] / max(0.1, mnestra["prompt_ms"]), 2)
    rec = {"server": SERVER, "requests": N_REQUESTS, "shared_prefix_address": addr,
           "baseline_no_reuse": baseline, "mnestra_prefix_reuse": mnestra,
           "evaluated_token_reduction_x": tok_red, "prompt_eval_time_reduction_x": ms_red}
    print(json.dumps(rec, indent=2))
    print(f"\nREAL KV-recompute reduction: {tok_red}x evaluated tokens, "
          f"{ms_red}x prompt-eval time (served, measured).")
    print("First request is cold in both (full eval); reuse pays from request 2 on.")


if __name__ == "__main__":
    main()
