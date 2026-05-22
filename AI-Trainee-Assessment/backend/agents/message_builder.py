"""Structured workflow message builder for multi-agent orchestration."""

from typing import Dict, Any, List, Optional


def workflow_message(
    agent: str,
    message: str,
    status: str = "processing",
    workflow_step: int = 1,
    direction: str = "relay",
    **extra: Any,
) -> Dict[str, Any]:
    """Build a structured agent workflow message for API and UI consumption."""
    payload: Dict[str, Any] = {
        "agent": agent,
        "message": message,
        "status": status,
        "workflow_step": workflow_step,
        "direction": direction,
    }
    payload.update(extra)
    return payload


def to_relay_entry(msg: Dict[str, Any]) -> Dict[str, str]:
    """Convert workflow message to legacy relay format (agent + message)."""
    return {"agent": msg["agent"], "message": msg["message"], "direction": msg.get("direction", "relay")}


def to_relay_chain(messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    return [to_relay_entry(m) for m in messages]
