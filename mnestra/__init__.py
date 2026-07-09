"""Mnestra — a substrate-agnostic, structure-complete memory fabric.

Read the whole book from any address; forward-compatible across classical, photonic, and
quantum hardware. See the docs/ for the scientific foundations and the logical model.
"""
from .backends import (Backend, ClassicalBackend, PhotonicHolographicBackend, AFCBackend,
                       content_address, embed, cosine)
from .codex import Codex, Slot
from .model import MnestraMemory
from .llm import MockLLM

__version__ = "0.1.0"
__all__ = ["MnestraMemory", "Codex", "Slot", "MockLLM", "Backend", "ClassicalBackend",
           "PhotonicHolographicBackend", "AFCBackend", "content_address", "embed", "cosine"]
