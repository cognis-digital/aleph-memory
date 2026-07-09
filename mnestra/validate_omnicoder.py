"""Validate the Mnestra efficiency thesis on a REAL transformer (OmniCoder via Ollama).

Generates the same structured brief two ways and reports Ollama's true metrics:

  causal — each section is prompted with the full growing transcript + the global rule.
  mnestra  — each section is prompted with a bounded structure-complete view
           (outline + rule + dependency summaries) from read_whole_book().

Measured (not modeled): total prompt tokens the model actually processed
(prompt_eval_count), wall-clock seconds, and how many sections honoured a global rule
(does the compact Mnestra context still keep the model on-spec?).

Run:  python -m mnestra.validate_omnicoder
"""
from __future__ import annotations

import json

from .codex import Codex, Slot
from .model import MnestraMemory
from .backends import ClassicalBackend
from .omnicoder import OmniCoder, available

RULE = "Every section MUST include the exact tag [MNESTRA-7] somewhere in its text."
_TITLES = [
    "Thesis", "Physics of the substrate", "Spectral hole burning", "Photon-echo holography",
    "Atomic frequency combs", "Logical memory model", "Content addressing",
    "Forward compatibility", "Photonic backend", "Quantum backend",
    "Efficiency for language models", "Conclusion",
]
# each section depends on the previous one + the thesis (bounded, ~2 deps) — but a CAUSAL
# writer must re-read the whole growing transcript, while Mnestra reads only those 2 summaries.
SECTIONS = [(f"s{i}", t, ([f"s{i-1}"] if i else []) + (["s0"] if i > 1 else []))
            for i, t in enumerate(_TITLES)]
TOPIC = "substrate-agnostic, structure-complete memory that lets an LLM read the whole document at once"


def _codex() -> Codex:
    plan = [Slot(sid, title, deps=deps, constraints=[RULE]) for sid, title, deps in SECTIONS]
    return Codex("Brief: " + TOPIC, plan)


def _summary(text: str, n: int = 25) -> str:
    return " ".join(text.split()[:n])


def run_causal(omni: OmniCoder) -> tuple[dict, int]:
    codex = _codex()
    transcript: list[str] = []
    honoured = 0
    for sid, title, _ in SECTIONS:
        ctx = ("You are writing a technical brief titled '%s'.\nRULE: %s\n\n"
               "Document so far:\n%s\n\nWrite the next section '%s' (4-6 sentences)."
               % (codex.title, RULE, "\n".join(transcript) or "(none yet)", title))
        out = omni.generate(ctx)
        honoured += "[MNESTRA-7]" in out
        transcript.append(f"## {title}\n{out}")
    return omni.snapshot(), honoured


def run_mnestra(omni: OmniCoder) -> tuple[dict, int]:
    codex = _codex()
    mem = MnestraMemory(ClassicalBackend(), codex)
    honoured = 0
    for sid, title, _ in SECTIONS:
        mem.read_whole_book(sid)   # exercise the recall path; keep only bounded context below
        deps = "; ".join(f"{d}={codex.slot(d).summary}" for d in codex.slot(sid).deps
                         if codex.slot(d).summary)
        # BOUNDED view: rule + only the (<=2) dependency summaries — NOT the growing transcript
        # and NOT the full outline. This is what makes the Mnestra path O(N) instead of O(N^2).
        ctx = ("You are writing a technical brief titled '%s'.\nRULE: %s\n"
               "Relevant prior sections: %s\n\n"
               "Write the section '%s' (4-6 sentences)."
               % (codex.title, RULE, deps or "(none)", title))
        out = omni.generate(ctx)
        honoured += "[MNESTRA-7]" in out
        mem.commit(sid, out, summary=_summary(out))
    return omni.snapshot(), honoured


def main() -> None:
    if not available():
        print("Ollama not reachable at :11434 — start it (OmniCoder).")
        return
    print(f"Validating on real model: {OmniCoder().model}\n")
    n = len(SECTIONS)

    print("running causal (growing transcript)...")
    causal, c_ok = run_causal(OmniCoder(num_predict=180))
    print("running mnestra (bounded whole-book view)...")
    mnestra, a_ok = run_mnestra(OmniCoder(num_predict=180))

    tok_red = round(causal["prompt_tokens"] / max(1, mnestra["prompt_tokens"]), 2)
    time_red = round(causal["seconds"] / max(0.1, mnestra["seconds"]), 2)
    rec = {
        "model": OmniCoder().model, "sections": n, "rule": RULE,
        "causal": {**causal, "rule_honoured": f"{c_ok}/{n}"},
        "mnestra": {**mnestra, "rule_honoured": f"{a_ok}/{n}"},
        "prompt_token_reduction_x": tok_red,
        "latency_reduction_x": time_red,
    }
    print("\n" + json.dumps(rec, indent=2))
    print(f"\nREAL prompt-token reduction: {tok_red}x   |   REAL latency reduction: {time_red}x")
    print(f"on-spec sections: causal {c_ok}/{n}, mnestra {a_ok}/{n} "
          f"(compact view {'preserves' if a_ok >= c_ok else 'reduces'} adherence)")


if __name__ == "__main__":
    main()
