"""Workflow Manager — relay orchestration state and conversation history."""

import uuid
from typing import Dict, Any, Optional, List
from enum import Enum


class OrchestrationPhase(str, Enum):
    TASK_RECEIVED = "task_received"
    RELAY_TO_FRONTEND = "relay_to_frontend"
    BACKEND_PROCESSING = "backend_processing"
    CLARIFICATION = "clarification"
    CONTENT_GENERATION = "content_generation"
    DELIVERY = "delivery"
    COMPLETED = "completed"


class WorkflowManager:
    """Maintains relay workflow state, conversation history, and active agent."""

    WORKFLOW_STEPS = [
        {"id": "task_received", "label": "Task Received"},
        {"id": "relay_frontend", "label": "Relay to Frontend"},
        {"id": "backend_processing", "label": "Backend Processing"},
        {"id": "clarification", "label": "Clarification"},
        {"id": "content_generation", "label": "Content Generation"},
        {"id": "delivery", "label": "Delivery to User"},
    ]

    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(self, user_prompt: str) -> str:
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = {
            "session_id": session_id,
            "user_prompt": user_prompt,
            "phase": OrchestrationPhase.TASK_RECEIVED.value,
            "active_agent": "Main Agent",
            "collected": {},
            "clarification_step": None,
            "conversation_history": [],
            "workflow_steps": [
                {**step, "status": "pending"} for step in self.WORKFLOW_STEPS
            ],
            "status": "active",
            "final_summary": None,
        }
        self._update_workflow_step(session_id, 0, "completed")
        self._update_workflow_step(session_id, 1, "active")
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self._sessions.get(session_id)

    def session_exists(self, session_id: str) -> bool:
        return session_id in self._sessions

    def set_active_agent(self, session_id: str, agent: str) -> None:
        session = self._sessions.get(session_id)
        if session:
            session["active_agent"] = agent

    def set_phase(self, session_id: str, phase: OrchestrationPhase) -> None:
        session = self._sessions.get(session_id)
        if session:
            session["phase"] = phase.value

    def set_clarification_step(self, session_id: str, field: str) -> None:
        session = self._sessions.get(session_id)
        if session:
            session["clarification_step"] = field
            session["collected"].setdefault(field, None)
            self.set_phase(session_id, OrchestrationPhase.CLARIFICATION)
            self._update_workflow_step(session_id, 2, "completed")
            self._update_workflow_step(session_id, 3, "active")

    def store_collected(self, session_id: str, field: str, value: str) -> None:
        session = self._sessions.get(session_id)
        if session:
            session["collected"][field] = value

    def append_history(self, session_id: str, messages: List[Dict[str, str]]) -> None:
        session = self._sessions.get(session_id)
        if session:
            session["conversation_history"].extend(messages)

    def mark_generating(self, session_id: str) -> None:
        self.set_phase(session_id, OrchestrationPhase.CONTENT_GENERATION)
        self._update_workflow_step(session_id, 3, "completed")
        self._update_workflow_step(session_id, 4, "active")

    def mark_completed(self, session_id: str) -> None:
        session = self._sessions.get(session_id)
        if session:
            session["phase"] = OrchestrationPhase.COMPLETED.value
            session["status"] = "completed"
            session["active_agent"] = "Main Agent"
            for i in range(4, len(session["workflow_steps"])):
                self._update_workflow_step(session_id, i, "completed")

    def get_workflow_steps(self, session_id: str) -> List[Dict[str, Any]]:
        session = self._sessions.get(session_id)
        return session["workflow_steps"] if session else []

    def _update_workflow_step(self, session_id: str, index: int, status: str) -> None:
        session = self._sessions.get(session_id)
        if session and 0 <= index < len(session["workflow_steps"]):
            session["workflow_steps"][index]["status"] = status
