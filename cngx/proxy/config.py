"""Proxy configuration."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ProxyConfig:
    host: str = "127.0.0.1"
    port: int = 8642
    default_task_id: str = "proxy"
    default_session_id: Optional[str] = None

    @classmethod
    def from_env(cls) -> "ProxyConfig":
        explicit = os.getenv("CNGX_SESSION_ID") or os.getenv("CNGX_PROXY_SESSION_ID")
        return cls(
            host=os.getenv("CNGX_PROXY_HOST", "127.0.0.1"),
            port=int(os.getenv("CNGX_PROXY_PORT", "8642")),
            default_task_id=os.getenv("CNGX_PROXY_TASK_ID", "proxy"),
            default_session_id=explicit.strip() if explicit else None,
        )

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


_config: ProxyConfig | None = None


def get_proxy_config() -> ProxyConfig:
    global _config
    if _config is None:
        _config = ProxyConfig.from_env()
    return _config
