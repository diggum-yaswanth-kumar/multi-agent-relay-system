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
    SYSTEM_ANALYSIS = "system_analysis"
    BACKEND_GENERATION = "backend_generation"
    FRONTEND_INTEGRATION = "frontend_integration"
    DELIVERY = "delivery"
    COMPLETED = "completed"


class WorkflowManager:
    """Maintains relay workflow state, conversation history, and active agent."""

    CONTENT_WORKFLOW_STEPS = [
        {"id": "task_received", "label": "Task Received"},
        {"id": "relay_frontend", "label": "Relay to Frontend"},
        {"id": "backend_processing", "label": "Backend Processing"},
        {"id": "clarification", "label": "Clarification"},
        {"id": "content_generation", "label": "Content Generation"},
        {"id": "delivery", "label": "Delivery to User"},
    ]

    SYSTEM_WORKFLOW_STEPS = [
        {"id": "task_received", "label": "Task Received"},
        {"id": "analysis", "label": "Requirement Analysis"},
        {"id": "backend_generation", "label": "Backend API Generation"},
        {"id": "frontend_integration", "label": "Frontend Integration"},
        {"id": "orchestration", "label": "Orchestration Complete"},
        {"id": "delivery", "label": "Final Delivery"},
    ]

    WORKFLOW_STEPS = CONTENT_WORKFLOW_STEPS

    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(
        self, user_prompt: str, workflow_type: str = "content_generation"
    ) -> str:
        session_id = str(uuid.uuid4())
        steps_template = (
            self.SYSTEM_WORKFLOW_STEPS
            if workflow_type == "system_orchestration"
            else self.CONTENT_WORKFLOW_STEPS
        )
        self._sessions[session_id] = {
            "session_id": session_id,
            "user_prompt": user_prompt,
            "workflow_type": workflow_type,
            "phase": OrchestrationPhase.TASK_RECEIVED.value,
            "active_agent": "Main Agent",
            "collected": {},
            "clarification_step": None,
            "conversation_history": [],
            "communication_logs": [],
            "workflow_steps": [
                {**step, "status": "pending"} for step in steps_template
            ],
            "completed_tasks": [],
            "status": "active",
            "final_summary": None,
        }
        self._update_workflow_step(session_id, 0, "completed")
        self._update_workflow_step(session_id, 1, "active")
        return session_id

    def log_communication(self, session_id: str, entry: Dict[str, Any]) -> None:
        session = self._sessions.get(session_id)
        if session:
            session["communication_logs"].append(entry)
            session["conversation_history"].append(
                {"agent": entry["agent"], "message": entry["message"]}
            )

    def complete_task(self, session_id: str, task_label: str) -> None:
        session = self._sessions.get(session_id)
        if session and task_label not in session["completed_tasks"]:
            session["completed_tasks"].append(task_label)

    def advance_system_step(self, session_id: str, step_index: int, phase: OrchestrationPhase) -> None:
        self.set_phase(session_id, phase)
        for i in range(step_index):
            self._update_workflow_step(session_id, i, "completed")
        self._update_workflow_step(session_id, step_index, "active")

    def mark_system_completed(self, session_id: str, final_summary: str = None) -> None:
        session = self._sessions.get(session_id)
        if session:
            session["phase"] = OrchestrationPhase.COMPLETED.value
            session["status"] = "completed"
            session["active_agent"] = "Main Agent"
            session["final_summary"] = final_summary
            for i in range(len(session["workflow_steps"])):
                self._update_workflow_step(session_id, i, "completed")

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
