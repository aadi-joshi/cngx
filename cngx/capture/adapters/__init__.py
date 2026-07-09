"""LLM adapters for cngx."""

from cngx.capture.adapters.base import BaseAdapter, StreamChunk
from cngx.capture.adapters.mock import MockAdapter


def __getattr__(name):
    """Lazy import optional adapters that require extra dependencies."""
    if name == "OpenAIAdapter":
        from cngx.capture.adapters.openai import OpenAIAdapter

        return OpenAIAdapter
    if name == "GeminiAdapter":
        from cngx.capture.adapters.gemini import GeminiAdapter

        return GeminiAdapter
    if name == "ClaudeAdapter":
        from cngx.capture.adapters.claude import ClaudeAdapter

        return ClaudeAdapter
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "BaseAdapter",
    "StreamChunk",
    "OpenAIAdapter",
    "MockAdapter",
    "GeminiAdapter",
    "ClaudeAdapter",
]
