"""Relay Manager — sequential multi-agent message chains and conversation history."""

from typing import Dict, Any, List, Optional


class RelayManager:
    """
    Builds strict relay chains:
    User → Main → Frontend → Backend → Frontend → Main → User
    """

    MAIN = "Main Agent"
    FRONTEND = "Frontend Agent"
    BACKEND = "Backend Agent"

    @staticmethod
    def entry(agent: str, message: str, direction: str = "relay") -> Dict[str, str]:
        return {"agent": agent, "message": message, "direction": direction}

    def build_start_chain(self, backend_clarification: Dict[str, Any]) -> List[Dict[str, str]]:
        """Initial request relay ending at Main Agent user question."""
        field = backend_clarification.get("field", "tone")
        return [
            self.entry(
                self.MAIN,
                "Task received. Frontend Agent, coordinate with Backend Agent.",
            ),
            self.entry(
                self.FRONTEND,
                "Backend Agent, content generation request initiated. "
                "Do you require clarification?",
            ),
            self.entry(self.BACKEND, backend_clarification["backend_message"]),
            self.entry(
                self.FRONTEND,
                f"Main Agent, Backend Agent requires {field} clarification.",
            ),
        ]

    def build_clarification_forward_chain(
        self, field: str, value: str, next_backend: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Relay user answer forward; ends with next backend need or generation trigger."""
        chains = [
            self.entry(
                self.MAIN,
                f"Frontend Agent, user selected {value.title()} {field}.",
            ),
            self.entry(
                self.FRONTEND,
                f"Backend Agent, {field} received: {value.title()}. "
                "Do you require additional clarification?",
            ),
        ]

        if next_backend.get("status") == "needs_clarification":
            chains.append(
                self.entry(self.BACKEND, next_backend["backend_message"])
            )
            chains.append(
                self.entry(
                    self.FRONTEND,
                    f"Main Agent, Backend Agent requires "
                    f"{next_backend['field']} clarification.",
                )
            )
        elif next_backend.get("status") == "ready_to_generate":
            chains.extend(self._generation_trigger_chain())
        return chains

    def build_completion_chain(self) -> List[Dict[str, str]]:
        """Final relay after backend generates content."""
        return [
            self.entry(self.BACKEND, "Content generation completed successfully."),
            self.entry(
                self.FRONTEND,
                "Main Agent, backend processing completed successfully.",
            ),
        ]

    def append_main_question(
        self, chain: List[Dict[str, str]], main_question: str
    ) -> List[Dict[str, str]]:
        """Append Main Agent user-facing question as final visible relay step."""
        if main_question:
            chain.append(self.entry(self.MAIN, main_question))
        return chain

    def _generation_trigger_chain(self) -> List[Dict[str, str]]:
        return [
            self.entry(
                self.FRONTEND,
                "Backend Agent, all required parameters collected. "
                "Generate final content.",
            ),
            self.entry(self.BACKEND, "Generating final content..."),
        ]

    def append_to_history(
        self, session: Dict[str, Any], messages: List[Dict[str, str]]
    ) -> None:
        if "conversation_history" not in session:
            session["conversation_history"] = []
        session["conversation_history"].extend(messages)
