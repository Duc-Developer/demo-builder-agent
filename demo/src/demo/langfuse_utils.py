from __future__ import annotations

import os
from contextlib import contextmanager, nullcontext
from typing import Any

from langfuse import Langfuse

_LANGFUSE_CLIENT: Langfuse | None = None
_LANGFUSE_DISABLED = False


def _build_client() -> Langfuse | None:
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "").strip().strip("\"'")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY", "").strip().strip("\"'")
    base_url = os.getenv("LANGFUSE_BASE_URL", "").strip().strip("\"'")

    if not public_key or not secret_key:
        return None

    kwargs: dict[str, Any] = {
        "public_key": public_key,
        "secret_key": secret_key,
    }
    if base_url:
        kwargs["base_url"] = base_url

    try:
        return Langfuse(**kwargs)
    except Exception:
        return None


def get_langfuse_client() -> Langfuse | None:
    global _LANGFUSE_CLIENT, _LANGFUSE_DISABLED

    if _LANGFUSE_DISABLED:
        return None
    if _LANGFUSE_CLIENT is not None:
        return _LANGFUSE_CLIENT

    client = _build_client()
    if client is None:
        _LANGFUSE_DISABLED = True
        return None

    _LANGFUSE_CLIENT = client
    return client


@contextmanager
def observe(name: str, *, input: Any = None, metadata: Any = None, as_type: str = "span"):
    client = get_langfuse_client()
    if client is None:
        with nullcontext(None) as span:
            yield span
        return

    try:
        with client.start_as_current_observation(
            name=name,
            input=input,
            metadata=metadata,
            as_type=as_type,
        ) as span:
            yield span
    except Exception:
        yield None


def update_observation(span: Any, **kwargs: Any) -> None:
    if span is None:
        return
    try:
        span.update(**kwargs)
    except Exception:
        return


def set_current_trace_io(*, input: Any = None, output: Any = None) -> None:
    client = get_langfuse_client()
    if client is None:
        return
    try:
        client.set_current_trace_io(input=input, output=output)
    except Exception:
        return


def get_current_trace_url() -> str | None:
    client = get_langfuse_client()
    if client is None:
        return None
    try:
        return client.get_trace_url()
    except Exception:
        return None


def flush_langfuse() -> None:
    client = get_langfuse_client()
    if client is None:
        return
    try:
        client.flush()
    except Exception:
        return


def healthcheck_langfuse() -> bool:
    client = get_langfuse_client()
    if client is None:
        return False
    try:
        return bool(client.auth_check())
    except Exception:
        return False
