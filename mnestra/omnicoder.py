"""Real-model adapter: drive a live transformer (OmniCoder via Ollama) and capture the
metrics that matter for the Mnestra thesis — the prompt tokens the model ACTUALLY processed
(`prompt_eval_count`) and wall-clock latency. Stdlib only.

This is what turns the modeled benchmark (mnestra.bench, a cost model) into a measurement on a
real transformer: causal generation feeds a growing transcript, Mnestra feeds a bounded
structure-complete view, and Ollama reports the true prompt-token count for each.
"""
from __future__ import annotations

import json
import time
import urllib.request

OLLAMA = "http://127.0.0.1:11434/api/chat"
MODEL = "zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF:latest"


class OmniCoder:
    """Live LLM with real token/latency accounting (sums across all calls)."""

    def __init__(self, model: str = MODEL, num_predict: int = 120, temperature: float = 0.2):
        self.model = model
        self.num_predict = num_predict
        self.temperature = temperature
        self.prompt_tokens = 0     # REAL prompt tokens processed (Ollama prompt_eval_count)
        self.gen_tokens = 0        # REAL generated tokens (eval_count)
        self.seconds = 0.0         # REAL wall-clock
        self.calls = 0

    def generate(self, prompt: str) -> str:
        body = json.dumps({
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"num_predict": self.num_predict, "temperature": self.temperature},
        }).encode()
        req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=600) as r:
            d = json.loads(r.read())
        self.seconds += time.time() - t0
        self.calls += 1
        self.prompt_tokens += int(d.get("prompt_eval_count", 0))
        self.gen_tokens += int(d.get("eval_count", 0))
        return d.get("message", {}).get("content", "")

    def snapshot(self) -> dict:
        return {"calls": self.calls, "prompt_tokens": self.prompt_tokens,
                "gen_tokens": self.gen_tokens, "seconds": round(self.seconds, 1)}


def available(timeout: float = 4.0) -> bool:
    try:
        urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=timeout)
        return True
    except Exception:
        return False
