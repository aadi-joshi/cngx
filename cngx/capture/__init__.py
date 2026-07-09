"""Trace capture module for cngx."""

from cngx.capture.adapters.base import BaseAdapter
from cngx.capture.adapters.mock import MockAdapter
from cngx.capture.tracer import CngxTracer


def __getattr__(name):
    """Lazy import optional adapters."""
    if name == "OpenAIAdapter":
        from cngx.capture.adapters.openai import OpenAIAdapter

        return OpenAIAdapter
    if name == "GeminiAdapter":
        from cngx.capture.adapters.gemini import GeminiAdapter

        return GeminiAdapter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "CngxTracer",
    "BaseAdapter",
    "OpenAIAdapter",
    "MockAdapter",
]
