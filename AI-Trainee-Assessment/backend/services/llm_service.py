"""LLM Service — OpenAI GPT-4o-mini content generation."""

import os
from pathlib import Path
from typing import Dict, Any, Optional

from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

# Load .env from backend directory or project root
_backend_dir = Path(__file__).resolve().parent.parent
_project_root = _backend_dir.parent
load_dotenv(_backend_dir / ".env")
load_dotenv(_project_root / ".env")

MODEL = "gpt-4o-mini"
DEFAULT_TIMEOUT = 60.0

LENGTH_GUIDANCE = {
    "short": "approximately 150–250 words (concise, 2–3 short paragraphs)",
    "medium": "approximately 400–550 words (balanced depth, several sections)",
    "long": "approximately 700–900 words (comprehensive, multiple sections)",
}

TONE_GUIDANCE = {
    "formal": "Use formal, polished language suitable for executive or academic audiences.",
    "casual": "Use a friendly, conversational tone that feels approachable and engaging.",
    "professional": (
        "Use a clear, professional business tone that is confident and actionable."
    ),
}

TASK_FORMAT = {
    "blog": "Write a well-structured blog post with a compelling title, introduction, body sections, and conclusion. Use markdown headings (##) for sections.",
    "article": "Write a structured article with clear sections and markdown headings.",
    "summary": "Write a concise executive summary with key takeaways.",
    "email": "Write a professional email draft with subject line, greeting, body, and sign-off.",
    "report": "Write a structured report with sections and markdown headings.",
    "content": "Write polished, well-organized content with appropriate structure.",
}


class LLMServiceError(Exception):
    """Raised when LLM generation fails."""

    def __init__(self, message: str, code: str = "llm_error"):
        self.message = message
        self.code = code
        super().__init__(message)


class LLMService:
    """Generates content via OpenAI GPT-4o-mini using structured prompts."""

    def __init__(self, api_key: Optional[str] = None, timeout: float = DEFAULT_TIMEOUT):
        self._api_key = api_key or os.getenv("OPENAI_API_KEY", "").strip()
        self._timeout = timeout
        self._client: Optional[OpenAI] = None

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key)

    def _get_client(self) -> OpenAI:
        if not self._api_key:
            raise LLMServiceError(
                "OpenAI API key is not configured. Add OPENAI_API_KEY to your .env file.",
                code="missing_api_key",
            )
        if self._client is None:
            self._client = OpenAI(api_key=self._api_key, timeout=self._timeout)
        return self._client

    def generate_content(self, task_context: Dict[str, Any]) -> str:
        """
        Generate content from collected task parameters.

        Args:
            task_context: topic, task_type, tone, length, original_request
        """
        topic = task_context.get("topic", "the requested subject")
        task_type = task_context.get("task_type", "content")
        tone = task_context.get("tone", "professional").lower()
        length = task_context.get("length", "medium").lower()
        original = task_context.get("original_request", "")

        if tone not in TONE_GUIDANCE:
            tone = "professional"
        if length not in LENGTH_GUIDANCE:
            length = "medium"

        system_prompt = (
            "You are an expert content writer. Generate high-quality, original content "
            "based on the user's specifications. Follow the requested tone, length, and format. "
            "Output only the final content — no meta-commentary about being an AI."
        )

        user_prompt = self._build_user_prompt(
            topic=topic,
            task_type=task_type,
            tone=tone,
            length=length,
            original_request=original,
        )

        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=self._max_tokens_for_length(length),
            )
        except AuthenticationError:
            raise LLMServiceError(
                "OpenAI authentication failed. Please verify your OPENAI_API_KEY.",
                code="auth_error",
            )
        except RateLimitError:
            raise LLMServiceError(
                "OpenAI rate limit reached. Please wait a moment and try again.",
                code="rate_limit",
            )
        except APITimeoutError:
            raise LLMServiceError(
                "Content generation timed out. Please try again with a shorter length.",
                code="timeout",
            )
        except APIConnectionError:
            raise LLMServiceError(
                "Could not connect to OpenAI. Check your network connection.",
                code="connection_error",
            )
        except APIStatusError as exc:
            raise LLMServiceError(
                f"OpenAI API error ({exc.status_code}). Please try again later.",
                code="api_error",
            )
        except LLMServiceError:
            raise
        except Exception as exc:
            raise LLMServiceError(
                f"Unexpected error during content generation: {exc}",
                code="unknown_error",
            )

        content = (response.choices[0].message.content or "").strip()
        if not content:
            raise LLMServiceError(
                "OpenAI returned an empty response. Please try again.",
                code="empty_response",
            )

        return content

    def _build_user_prompt(
        self,
        topic: str,
        task_type: str,
        tone: str,
        length: str,
        original_request: str,
    ) -> str:
        format_instruction = TASK_FORMAT.get(task_type, TASK_FORMAT["content"])
        return (
            f"Create content based on the following specifications:\n\n"
            f"Topic: {topic}\n"
            f"Tone: {tone.title()}\n"
            f"Length: {length.title()} — {LENGTH_GUIDANCE[length]}\n"
            f"Content type: {task_type}\n\n"
            f"Tone guidance: {TONE_GUIDANCE[tone]}\n\n"
            f"Format: {format_instruction}\n\n"
            f"Original user request: \"{original_request}\"\n\n"
            f"Generate professional content accordingly."
        )

    @staticmethod
    def _max_tokens_for_length(length: str) -> int:
        return {"short": 500, "medium": 1200, "long": 2000}.get(length, 1200)
