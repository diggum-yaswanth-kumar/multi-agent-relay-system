"""Main Agent — user-facing orchestrator; relay-only communication with Frontend Agent."""

from typing import Dict, Any, List

from agents.workflow_manager import WorkflowManager, OrchestrationPhase
from agents.frontend_agent import FrontendAgent
from agents.relay_manager import RelayManager


class OrchestratorAgent:
    """
    Main Agent (Orchestrator):
    - Communicates ONLY with User and Frontend Agent
    - Initiates workflow and delivers final responses
    - Requests clarification from user (relayed from Backend via Frontend)
    """

    AGENT_NAME = RelayManager.MAIN

    def __init__(self, workflow_manager: WorkflowManager, frontend_agent: FrontendAgent):
        self.workflow_manager = workflow_manager
        self.frontend_agent = frontend_agent
        self.relay = RelayManager()

    def start_orchestration(self, user_message: str) -> Dict[str, Any]:
        """
        User → Main → Frontend → Backend → Frontend → Main → User
        """
        message = user_message.strip()
        if not message:
            return self._error("Please provide a content generation request.")

        session_id = self.workflow_manager.create_session(message)
        self.workflow_manager.set_phase(session_id, OrchestrationPhase.RELAY_TO_FRONTEND)
        self.workflow_manager.set_active_agent(session_id, self.AGENT_NAME)

        backend_payload = self.frontend_agent.forward_content_request(
            message, session_id
        )
        relayed = self.frontend_agent.relay_backend_response(backend_payload)

        relay_messages = self.relay.build_start_chain(relayed)
        self.relay.append_main_question(relay_messages, relayed["main_question"])
        self.workflow_manager.append_history(session_id, relay_messages)
        self.workflow_manager.set_clarification_step(session_id, relayed["field"])
        self.workflow_manager.set_active_agent(session_id, self.AGENT_NAME)

        return self._build_response(
            status="needs_clarification",
            session_id=session_id,
            relay_messages=relay_messages,
            question=relayed["main_question"],
            field=relayed["field"],
            metadata=relayed.get("metadata"),
        )

    def process_clarification(
        self, session_id: str, field: str, value: str
    ) -> Dict[str, Any]:
        """Relay user answer through Frontend Agent to Backend Agent."""
        if not self.workflow_manager.session_exists(session_id):
            return self._error("Invalid or expired session.")

        self.workflow_manager.store_collected(session_id, field, value)
        relay_messages: List[Dict[str, str]] = []

        backend_payload = self.frontend_agent.forward_clarification(
            session_id, field, value
        )

        if backend_payload.get("status") == "needs_clarification":
            relayed = self.frontend_agent.relay_backend_response(backend_payload)
            relay_messages = self.relay.build_clarification_forward_chain(
                field, value, relayed
            )
            self.relay.append_main_question(relay_messages, relayed["main_question"])
            self.workflow_manager.append_history(session_id, relay_messages)
            self.workflow_manager.set_clarification_step(session_id, relayed["field"])

            return self._build_response(
                status="needs_clarification",
                session_id=session_id,
                relay_messages=relay_messages,
                question=relayed["main_question"],
                field=relayed["field"],
                metadata=relayed.get("metadata"),
            )

        if backend_payload.get("status") == "ready_to_generate":
            relay_messages = self.relay.build_clarification_forward_chain(
                field, value, backend_payload
            )
            self.workflow_manager.mark_generating(session_id)
            self.workflow_manager.append_history(session_id, relay_messages)

            gen_result = self.frontend_agent.backend_agent.generate_content(session_id)

            if gen_result.get("status") == "error":
                error_msg = gen_result.get(
                    "message",
                    "Content generation failed. Please try again.",
                )
                relay_messages.append(
                    self.relay.entry(
                        self.AGENT_NAME,
                        f"Content generation could not be completed: {error_msg}",
                    )
                )
                self.workflow_manager.append_history(session_id, relay_messages)
                return self._build_response(
                    status="error",
                    session_id=session_id,
                    relay_messages=relay_messages,
                    message=error_msg,
                )

            completion_relay = self.relay.build_completion_chain()
            relay_messages.extend(completion_relay)
            self.workflow_manager.append_history(session_id, completion_relay)
            self.workflow_manager.mark_completed(session_id)

            meta = gen_result.get("metadata", {})
            task_type = meta.get("task_type", "content")
            main_delivery = (
                "Here is your generated blog."
                if task_type == "blog"
                else f"Here is your generated {task_type}."
            )
            relay_messages.append(self.relay.entry(self.AGENT_NAME, main_delivery))

            return self._build_response(
                status="completed",
                session_id=session_id,
                relay_messages=relay_messages,
                result=gen_result.get("result"),
                metadata=gen_result.get("metadata"),
                message=main_delivery,
            )

        return self._error(backend_payload.get("message", "Processing failed."))

    def _build_response(
        self,
        status: str,
        session_id: str,
        relay_messages: List[Dict[str, str]],
        question: str = None,
        field: str = None,
        result: str = None,
        metadata: Dict[str, Any] = None,
        message: str = None,
    ) -> Dict[str, Any]:
        session = self.workflow_manager.get_session(session_id)
        return {
            "status": status,
            "agent": self.AGENT_NAME,
            "session_id": session_id,
            "question": question,
            "field": field,
            "result": result,
            "message": message,
            "metadata": {
                **(metadata or {}),
                "active_agent": session.get("active_agent") if session else self.AGENT_NAME,
                "collected": session.get("collected", {}) if session else {},
                "clarification_step": session.get("clarification_step") if session else field,
                "phase": session.get("phase") if session else None,
            },
            "main_agent": self.AGENT_NAME,
            "relay_messages": relay_messages,
            "orchestration_logs": relay_messages,
            "workflow_steps": self.workflow_manager.get_workflow_steps(session_id),
            "workflow_phase": session.get("phase") if session else None,
            "conversation_history": session.get("conversation_history", []) if session else [],
        }

    def _error(self, message: str) -> Dict[str, Any]:
        return {
            "status": "error",
            "agent": self.AGENT_NAME,
            "message": message,
            "relay_messages": [
                self.relay.entry(self.AGENT_NAME, f"Error: {message}")
            ],
            "orchestration_logs": [
                self.relay.entry(self.AGENT_NAME, f"Error: {message}")
            ],
        }
