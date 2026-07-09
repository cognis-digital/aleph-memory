"""Tests for the Mnestra reference implementation."""
import pytest

from mnestra import (MnestraMemory, Codex, Slot, MockLLM, content_address,
                   ClassicalBackend, PhotonicHolographicBackend, AFCBackend)
from mnestra.bench import benchmark, make_codex


def _codex():
    return Codex("t", [Slot("s0", "intro", shared_facts=["f0"]),
                       Slot("s1", "body", deps=["s0"]),
                       Slot("s2", "end", deps=["s0", "s1"], constraints=["c0"])])


def test_content_address_stable():
    assert content_address({"a": 1, "b": 2}) == content_address({"b": 2, "a": 1})
    assert content_address("x") != content_address("y")


@pytest.mark.parametrize("backend", [ClassicalBackend(), PhotonicHolographicBackend(), AFCBackend()])
def test_backend_roundtrip_and_recall(backend):
    m = MnestraMemory(backend, _codex())
    m.commit("s0", "photons and coherence in crystals", "photon intro")
    m.commit("s1", "spin states and storage time", "spin body")
    view = m.read_whole_book("s2")
    assert view["total"] == 3 and view["filled"] == 2
    assert view["recalled"] and view["recalled"][0]["score"] >= view["recalled"][-1]["score"]


def test_reconstruct_is_structure_complete():
    m = MnestraMemory(ClassicalBackend(), _codex())
    m.commit("s0", "a", "sa")
    assert m.reconstruct()["records"] >= 2  # plan + slot, recoverable globally


def test_photonic_capacity_guard():
    b = PhotonicHolographicBackend(channels=1)
    b.write("a", {"text": "x"})
    with pytest.raises(MemoryError):
        b.write("b", {"text": "y"})


def test_afc_efficiency_monotonic():
    assert AFCBackend(finesse=2).efficiency() < AFCBackend(finesse=20).efficiency()


def test_memo_skips_recompute():
    llm = MockLLM()
    a = llm.derive_fact("f", memoized=True)
    calls_after_first = llm.calls
    b = llm.derive_fact("f", memoized=True)
    assert a == b and llm.calls == calls_after_first  # second derivation served from memo


def test_benchmark_shows_efficiency_gain():
    r = benchmark(n_slots=40)
    assert r["work_speedup_x"] > 1.0
    assert r["recomputes_avoided"] > 0
    assert r["retries_avoided"] > 0
    assert r["mnestra"]["work_tokens"] < r["causal"]["work_tokens"]


def test_speedup_grows_with_scale():
    assert benchmark(100)["work_speedup_x"] > benchmark(10)["work_speedup_x"]


def test_fabric_composes_and_dedups():
    from mnestra.fabric import demo
    s = demo()
    assert s["prefix_hit_rate"] > 0.5          # shared system prompt reused
    assert s["kv_dedup_ratio"] > 1.0           # identical KV pages collapse
    assert s["kv_pages_physical"] < s["kv_pages_logical"]
    assert s["tiers_served"]["generate"] == 0  # every request served from a tier


def test_fabric_is_substrate_agnostic():
    from mnestra.fabric import Fabric
    from mnestra.backends import PhotonicHolographicBackend
    fab = Fabric(PhotonicHolographicBackend(channels=64))
    fab.ingest("photonic quantum memory note", "n")
    out = fab.serve({"prefix": ["a", "b"], "body": ["c"], "query": "quantum memory"})
    assert out["served_by"]  # same fabric API over a different substrate
