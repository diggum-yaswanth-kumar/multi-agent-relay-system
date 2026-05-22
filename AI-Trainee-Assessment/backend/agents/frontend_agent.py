"""Frontend Agent — communication mediator between Main Agent and Backend Agent."""

from typing import Dict, Any, List

from agents.backend_agent import BackendAgent
from agents.relay_manager import RelayManager


class FrontendAgent:
    """
    Frontend Agent acts ONLY as relay mediator:
    - Receives from Main Agent → forwards to Backend Agent
    - Receives from Backend Agent → forwards to Main Agent
    - Never communicates directly with User
    """

    AGENT_NAME = RelayManager.FRONTEND

    def __init__(self, backend_agent: BackendAgent):
        self.backend_agent = backend_agent
        self.relay = RelayManager()

    def forward_content_request(self, user_message: str, session_id: str) -> Dict[str, Any]:
        """Relay content request from Main Agent to Backend Agent."""
        return self.backend_agent.initiate_content_processing(
            user_message, session_id=session_id
        )

    def forward_clarification(
        self, session_id: str, field: str, value: str
    ) -> Dict[str, Any]:
        """Relay user-provided clarification from Main Agent to Backend Agent."""
        return self.backend_agent.process_parameter(session_id, field, value)

    def simulate_frontend_integration(
        self, api_contract: Dict[str, Any], session_id: str
    ) -> Dict[str, Any]:
        """Simulate frontend integration with backend API contract."""
        system_name = api_contract.get("system_name", "Application")
        integrated_components = [
            "ChatWindow → POST /api/agent/start",
            "InputArea → POST /api/agent/respond",
            "AgentDashboard → GET /api/health",
            "WorkflowProgress → workflow_steps payload",
            "CommunicationFeed → relay_messages stream",
        ]
        return {
            "status": "integration_complete",
            "session_id": session_id,
            "system_name": system_name,
            "integrated_components": integrated_components,
            "frontend_message": (
                "Received backend API configuration.\n\n"
                "Integrating frontend components with backend APIs..."
            ),
            "completion_message": "Frontend integration completed successfully.",
            "metadata": {
                "step": "frontend_integration",
                "api_base": api_contract.get("base_url"),
            },
        }

    def relay_backend_response(self, backend_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Package Backend Agent response for Main Agent (never user-direct)."""
        return {
            "status": backend_payload.get("status"),
            "field": backend_payload.get("field"),
            "backend_message": backend_payload.get("backend_message"),
            "main_question": backend_payload.get("main_question"),
            "result": backend_payload.get("result"),
            "metadata": backend_payload.get("metadata"),
            "session_id": backend_payload.get("session_id"),
        }
