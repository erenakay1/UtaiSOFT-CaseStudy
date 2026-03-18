"""Node: execute_tool — Runs the selected tool with extracted params.

Includes retry logic with exponential backoff for transient failures
(network errors, API rate limits, timeouts).
"""

from __future__ import annotations

import logging
import time

import config
from agent.state import AgentState
from registry.registry import ToolRegistry

logger = logging.getLogger(__name__)

# The registry is injected at graph-build time (see graph.py)
_registry: ToolRegistry | None = None

# Errors that should NOT be retried (bad input, logic errors)
_NON_RETRYABLE = (ValueError, KeyError, TypeError, AttributeError)


def set_registry(registry: ToolRegistry) -> None:
    """Called once at startup to inject the active registry."""
    global _registry
    _registry = registry


def _invoke_with_retry(instance, params: dict, tool_name: str) -> str:
    """Execute a tool with exponential backoff retry on transient errors.

    Retry strategy:
        - Max attempts : config.TOOL_RETRY_MAX_ATTEMPTS (default 3)
        - Base delay   : config.TOOL_RETRY_BASE_DELAY   (default 1s)
        - Delay formula: base_delay * 2^(attempt - 1)   → 1s, 2s, 4s …
        - Non-retryable errors (ValueError, KeyError, …) fail immediately.
    """
    max_attempts = config.TOOL_RETRY_MAX_ATTEMPTS
    base_delay = config.TOOL_RETRY_BASE_DELAY
    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            result = instance.invoke(params)
            if attempt > 1:
                logger.info(
                    "Tool '%s' succeeded on attempt %d/%d",
                    tool_name, attempt, max_attempts,
                )
            return str(result)
        except _NON_RETRYABLE as e:
            # Bad input / logic error — retrying won't help
            logger.warning("Non-retryable error for '%s': %s", tool_name, e)
            raise
        except Exception as e:
            last_error = e
            if attempt < max_attempts:
                delay = base_delay * (2 ** (attempt - 1))
                logger.warning(
                    "Tool '%s' failed (attempt %d/%d): %s — retrying in %.1fs",
                    tool_name, attempt, max_attempts, e, delay,
                )
                time.sleep(delay)
            else:
                logger.error(
                    "Tool '%s' failed after %d attempts: %s",
                    tool_name, max_attempts, e,
                )

    raise last_error  # type: ignore[misc]


def execute_tool(state: AgentState) -> dict:
    """Invoke the selected tool and capture the result."""
    tool_name = state.get("selected_tool")
    params = state.get("tool_params", {})

    if not tool_name or _registry is None:
        return {"tool_result": "Tool bulunamadı veya seçilemedi."}

    instance = _registry.get_instance(tool_name)
    if instance is None:
        return {"tool_result": f"'{tool_name}' tool'u registry'de bulunamadı."}

    try:
        result = _invoke_with_retry(instance, params, tool_name)
        return {"tool_result": result}
    except Exception as e:
        return {"tool_result": f"Tool çalıştırma hatası ({tool_name}): {e}"}
