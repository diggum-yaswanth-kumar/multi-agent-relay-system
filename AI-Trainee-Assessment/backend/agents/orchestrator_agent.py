"""Main Agent — user-facing orchestrator; relay-only communication with Frontend Agent."""

from typing import Dict, Any, List

from agents.workflow_manager import WorkflowManager, OrchestrationPhase
from agents.frontend_agent import FrontendAgent
from agents.relay_manager import RelayManager
from agents.task_classifier import classify_task, WorkflowType
from agents.message_builder import to_relay_chain


class OrchestratorAgent:
    """
    Main Agent (Orchestrator):
    - Communicates ONLY with User and Frontend Agent
    - Routes content generation vs system orchestration workflows
    - Initiates workflow, delegates tasks, monitors completion
    """

    AGENT_NAME = RelayManager.MAIN

    def __init__(self, workflow_manager: WorkflowManager, frontend_agent: FrontendAgent):
        self.workflow_manager = workflow_manager
        self.frontend_agent = frontend_agent
        self.relay = RelayManager()

    def start_orchestration(self, user_message: str) -> Dict[str, Any]:
        """Route user request to the appropriate multi-agent workflow."""
        message = user_message.strip()
        if not message:
            return self._error("Please provide a task or content request.")

        workflow_type = classify_task(message)
        if workflow_type == WorkflowType.SYSTEM_ORCHESTRATION:
            return self._start_system_orchestration(message)
        return self._start_content_orchestration(message)

    def _start_system_orchestration(self, user_message: str) -> Dict[str, Any]:
        """Simulated full-stack system build orchestration workflow."""
        session_id = self.workflow_manager.create_session(
            user_message, workflow_type="system_orchestration"
        )
        self.workflow_manager.set_active_agent(session_id, self.AGENT_NAME)
        self.workflow_manager.advance_system_step(
            session_id, 2, OrchestrationPhase.BACKEND_GENERATION
        )

        backend_result = self.frontend_agent.backend_agent.simulate_backend_generation(
            user_message, session_id
        )
        self.workflow_manager.complete_task(session_id, "backend_api_generation")
        self.workflow_manager.advance_system_step(
            session_id, 3, OrchestrationPhase.FRONTEND_INTEGRATION
        )

        frontend_result = self.frontend_agent.simulate_frontend_integration(
            backend_result["api_contract"], session_id
        )
        self.workflow_manager.complete_task(session_id, "frontend_integration")

        workflow_messages = self.relay.build_system_orchestration_chain(
            backend_result, frontend_result
        )
        relay_messages = to_relay_chain(workflow_messages)

        for msg in workflow_messages:
            self.workflow_manager.log_communication(session_id, msg)

        deliverable = self.frontend_agent.backend_agent.build_system_deliverable(
            user_message,
            backend_result["api_contract"],
            frontend_result,
        )
        self.workflow_manager.mark_system_completed(session_id, deliverable)

        return self._build_response(
            status="completed",
            session_id=session_id,
            workflow_messages=workflow_messages,
            relay_messages=relay_messages,
            result=deliverable,
            message="Workflow orchestration completed successfully.",
            metadata={
                "workflow_type": "system_orchestration",
                "system_name": backend_result.get("system_name"),
                "api_contract": backend_result.get("api_contract"),
                "integration": frontend_result,
            },
        )

    def _start_content_orchestration(self, user_message: str) -> Dict[str, Any]:
        """User → Main → Frontend → Backend → Frontend → Main → User (content flow)."""
        session_id = self.workflow_manager.create_session(user_message)
        self.workflow_manager.set_phase(session_id, OrchestrationPhase.RELAY_TO_FRONTEND)
        self.workflow_manager.set_active_agent(session_id, self.AGENT_NAME)

        backend_payload = self.frontend_agent.forward_content_request(
            user_message, session_id
        )
        relayed = self.frontend_agent.relay_backend_response(backend_payload)

        relay_messages = self.relay.build_start_chain(relayed)
        self.relay.append_main_question(relay_messages, relayed["main_question"])
        self.workflow_manager.append_history(session_id, relay_messages)
        self.workflow_manager.set_clarification_step(session_id, relayed["field"])
        self.workflow_manager.set_active_agent(session_id, self.AGENT_NAME)

        workflow_messages = [
            {**m, "status": "processing", "workflow_step": i + 1}
            for i, m in enumerate(relay_messages)
        ]

        return self._build_response(
            status="needs_clarification",
            session_id=session_id,
            relay_messages=relay_messages,
            workflow_messages=workflow_messages,
            question=relayed["main_question"],
            field=relayed["field"],
            metadata={
                **(relayed.get("metadata") or {}),
                "workflow_type": "content_generation",
            },
        )

    def process_clarification(
        self, session_id: str, field: str, value: str
    ) -> Dict[str, Any]:
        """Relay user answer through Frontend Agent to Backend Agent."""
        if not self.workflow_manager.session_exists(session_id):
            return self._error("Invalid or expired session.")

        session = self.workflow_manager.get_session(session_id)
        if session and session.get("workflow_type") == "system_orchestration":
            return self._error("This session does not accept clarifications.")

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

            workflow_messages = [
                {**m, "status": "processing", "workflow_step": i + 1}
                for i, m in enumerate(relay_messages)
            ]

            return self._build_response(
                status="needs_clarification",
                session_id=session_id,
                relay_messages=relay_messages,
                workflow_messages=workflow_messages,
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

            workflow_messages = [
                {**m, "status": "processing", "workflow_step": i + 1}
                for i, m in enumerate(relay_messages[:-1])
            ]
            workflow_messages.append({
                "agent": self.AGENT_NAME,
                "message": main_delivery,
                "status": "completed",
                "workflow_step": len(relay_messages),
            })

            return self._build_response(
                status="completed",
                session_id=session_id,
                relay_messages=relay_messages,
                workflow_messages=workflow_messages,
                result=gen_result.get("result"),
                metadata=gen_result.get("metadata"),
                message=main_delivery,
            )

        return self._error(backend_payload.get("message", "Processing failed."))

    def _build_response(
        self,
        status: str,
        session_id: str,
        relay_messages: List[Dict[str, str]] = None,
        workflow_messages: List[Dict[str, Any]] = None,
        question: str = None,
        field: str = None,
        result: str = None,
        metadata: Dict[str, Any] = None,
        message: str = None,
    ) -> Dict[str, Any]:
        session = self.workflow_manager.get_session(session_id)
        relay = relay_messages or []
        wf_msgs = workflow_messages or [
            {**m, "status": status, "workflow_step": i + 1}
            for i, m in enumerate(relay)
        ]
        active = session.get("active_agent") if session else self.AGENT_NAME

        return {
            "status": status,
            "agent": self.AGENT_NAME,
            "session_id": session_id,
            "question": question,
            "field": field,
            "result": result,
            "message": message or (wf_msgs[-1]["message"] if wf_msgs else None),
            "metadata": {
                **(metadata or {}),
                "active_agent": active,
                "collected": session.get("collected", {}) if session else {},
                "clarification_step": session.get("clarification_step") if session else field,
                "phase": session.get("phase") if session else None,
                "workflow_type": session.get("workflow_type") if session else None,
                "completed_tasks": session.get("completed_tasks", []) if session else [],
            },
            "main_agent": self.AGENT_NAME,
            "relay_messages": relay,
            "workflow_messages": wf_msgs,
            "orchestration_logs": relay,
            "communication_logs": session.get("communication_logs", wf_msgs) if session else wf_msgs,
            "workflow_steps": self.workflow_manager.get_workflow_steps(session_id),
            "workflow_phase": session.get("phase") if session else None,
            "conversation_history": session.get("conversation_history", []) if session else [],
            "orchestration_summary": message,
        }

    def _error(self, message: str) -> Dict[str, Any]:
        wf = [{
            "agent": self.AGENT_NAME,
            "message": f"Error: {message}",
            "status": "error",
            "workflow_step": 1,
        }]
        relay = [self.relay.entry(self.AGENT_NAME, f"Error: {message}")]
        return {
            "status": "error",
            "agent": self.AGENT_NAME,
            "message": message,
            "relay_messages": relay,
            "workflow_messages": wf,
            "orchestration_logs": relay,
            "communication_logs": wf,
        }
