"""Backend Agent — content processing; communicates ONLY via Frontend Agent relay."""

import re
from typing import Dict, Any, Optional

from agents.task_manager import TaskManager, WorkflowStep
from services.llm_service import LLMService, LLMServiceError


class BackendAgent:
    """
    Backend Agent responsibilities:
    - Content processing and parameter validation
    - Internal clarification requests (relayed through Frontend → Main → User)
    - Final content generation
    """

    AGENT_NAME = "Backend Agent"

    VALID_TONES = {"formal", "casual", "professional"}
    VALID_LENGTHS = {"short", "medium", "long"}

    INTERNAL_CLARIFICATIONS = {
        "tone": {
            "backend_message": (
                "Please ask the user what tone they prefer:\n"
                "- Formal\n- Casual\n- Professional"
            ),
            "main_question": "What tone would you like?",
        },
        "length": {
            "backend_message": (
                "Please ask the user what content length they prefer:\n"
                "- Short\n- Medium\n- Long"
            ),
            "main_question": "What content length would you like?",
        },
    }

    TASK_PATTERNS = {
        "blog": r"\b(blog|post|write\s+about)\b",
        "article": r"\b(article|piece|publish)\b",
        "summary": r"\b(summary|summarize|overview|brief)\b",
        "email": r"\b(email|mail|message\s+to)\b",
        "report": r"\b(report|analysis|document)\b",
    }

    def __init__(self, task_manager: TaskManager, llm_service: LLMService):
        self.task_manager = task_manager
        self.llm_service = llm_service

    def analyze_request(self, message: str) -> Dict[str, Any]:
        message_lower = message.lower()
        task_type = "content"
        for ttype, pattern in self.TASK_PATTERNS.items():
            if re.search(pattern, message_lower):
                task_type = ttype
                break
        topic = self._extract_topic(message)
        return {
            "task_type": task_type,
            "topic": topic,
            "missing_parameters": ["tone", "length"],
            "analysis_summary": (
                f"Detected {task_type} request about '{topic}'. "
                "Requires tone and length clarification."
            ),
        }

    def _extract_topic(self, message: str) -> str:
        patterns = [
            r"(?:blog|article|report|email|summary)\s+(?:about|on)\s+(.+?)(?:\.|$)",
            r"(?:create|write|generate|draft)\s+(?:a\s+)?(?:\w+\s+)?(?:about|on)\s+(.+?)(?:\.|$)",
            r"(?:about|on|regarding|for)\s+(.+?)(?:\.|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                topic = match.group(1).strip()
                topic = re.sub(
                    r"^(?:a\s+)?(?:blog|article|report|email|summary)\s+(?:about|on)\s+",
                    "",
                    topic,
                    flags=re.IGNORECASE,
                )
                if len(topic) > 3:
                    return topic[:120]
        words = message.split()
        if len(words) > 4:
            return " ".join(words[-6:])[:120]
        return message[:80] if message else "general topic"

    def _clarification_payload(
        self, session_id: str, field: str, analysis: Optional[Dict] = None
    ) -> Dict[str, Any]:
        spec = self.INTERNAL_CLARIFICATIONS[field]
        meta = {"step": f"awaiting_{field}", "field": field}
        if analysis:
            meta.update({
                "analysis": analysis["analysis_summary"],
                "task_type": analysis["task_type"],
                "topic": analysis["topic"],
            })
        return {
            "status": "needs_clarification",
            "session_id": session_id,
            "field": field,
            "backend_message": spec["backend_message"],
            "main_question": spec["main_question"],
            "metadata": meta,
        }

    def initiate_content_processing(
        self, user_message: str, session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Begin processing; request tone via relay (never direct to user)."""
        analysis = self.analyze_request(user_message)
        session_id = self.task_manager.create_session(
            user_message, analysis, session_id=session_id
        )
        return self._clarification_payload(session_id, "tone", analysis)

    def process_parameter(
        self, session_id: str, field: str, value: str
    ) -> Dict[str, Any]:
        """Process relayed parameter; return next clarification or ready_to_generate."""
        session = self.task_manager.get_session(session_id)
        if not session:
            return self._error("Invalid or expired session.")

        normalized = value.strip().lower()

        if field == "tone":
            if normalized not in self.VALID_TONES:
                return self._clarification_payload(session_id, "tone")
            self.task_manager.update_parameter(session_id, "tone", normalized)
            return self._clarification_payload(session_id, "length")

        if field == "length":
            if normalized not in self.VALID_LENGTHS:
                return self._clarification_payload(session_id, "length")
            self.task_manager.update_parameter(session_id, "length", normalized)
            return {"status": "ready_to_generate", "session_id": session_id}

        return self._error(f"Unknown clarification field: {field}")

    def generate_content(self, session_id: str) -> Dict[str, Any]:
        """Generate final content via GPT-4o-mini after all parameters collected."""
        context = self.task_manager.get_task_context(session_id)
        if not context:
            return self._error("Unable to build task context.")

        try:
            result = self.llm_service.generate_content(context)
        except LLMServiceError as exc:
            return self._error(exc.message)

        self.task_manager.mark_completed(session_id, result)

        return {
            "status": "completed",
            "session_id": session_id,
            "result": result,
            "metadata": {
                "task_type": context["task_type"],
                "topic": context["topic"],
                "tone": context["tone"],
                "length": context["length"],
                "step": WorkflowStep.COMPLETED.value,
                "model": "gpt-4o-mini",
                "generation_source": "openai",
            },
        }

    def _error(self, message: str) -> Dict[str, Any]:
        return {"status": "error", "message": message}
