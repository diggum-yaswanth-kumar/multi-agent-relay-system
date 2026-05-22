"""Task Manager — orchestrates workflow state across agent sessions."""

import uuid
from typing import Dict, Any, Optional
from enum import Enum


class WorkflowStep(str, Enum):
    INIT = "init"
    AWAITING_TONE = "awaiting_tone"
    AWAITING_LENGTH = "awaiting_length"
    GENERATING = "generating"
    COMPLETED = "completed"


class TaskManager:
    """
    Central state manager for multi-step agent workflows.
    Maintains sessions, steps, and collected parameters.
    """

    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(
        self,
        user_message: str,
        analyzed_task: Dict[str, Any],
        session_id: Optional[str] = None,
    ) -> str:
        """Initialize a new workflow session."""
        session_id = session_id or str(uuid.uuid4())
        self._sessions[session_id] = {
            "session_id": session_id,
            "original_request": user_message,
            "task_type": analyzed_task.get("task_type", "content"),
            "topic": analyzed_task.get("topic", "general topic"),
            "current_step": WorkflowStep.AWAITING_TONE.value,
            "collected": {},
            "status": "active",
        }
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session state by ID."""
        return self._sessions.get(session_id)

    def update_parameter(self, session_id: str, field: str, value: str) -> bool:
        """Store a clarification response and advance workflow step."""
        session = self._sessions.get(session_id)
        if not session:
            return False

        session["collected"][field] = value.strip()

        if field == "tone":
            session["current_step"] = WorkflowStep.AWAITING_LENGTH.value
        elif field == "length":
            session["current_step"] = WorkflowStep.GENERATING.value

        return True

    def mark_completed(self, session_id: str, result: str) -> None:
        """Mark session as completed with final generated content."""
        session = self._sessions.get(session_id)
        if session:
            session["current_step"] = WorkflowStep.COMPLETED.value
            session["status"] = "completed"
            session["final_result"] = result

    def get_task_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Build full context dict for content generation."""
        session = self._sessions.get(session_id)
        if not session:
            return None

        return {
            "topic": session["topic"],
            "task_type": session["task_type"],
            "tone": session["collected"].get("tone", "professional"),
            "length": session["collected"].get("length", "medium"),
            "original_request": session["original_request"],
        }

    def session_exists(self, session_id: str) -> bool:
        return session_id in self._sessions
