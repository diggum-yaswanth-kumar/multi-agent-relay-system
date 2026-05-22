"""Task Classifier — routes requests to content vs system orchestration workflows."""

import re
from enum import Enum


class WorkflowType(str, Enum):
    CONTENT_GENERATION = "content_generation"
    SYSTEM_ORCHESTRATION = "system_orchestration"


SYSTEM_BUILD_PATTERNS = [
    r"\bbuild\b.*\b(system|platform|application|app|service|api)\b",
    r"\b(create|develop|design|implement)\b.*\b(system|platform|application)\b",
    r"\bblog\s+generation\s+system\b",
    r"\bgeneration\s+system\b",
    r"\b(full[- ]?stack|end[- ]?to[- ]?end)\b.*\b(build|system)\b",
]


def classify_task(message: str) -> WorkflowType:
    """Determine which orchestration workflow applies to the user request."""
    text = message.strip().lower()
    for pattern in SYSTEM_BUILD_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return WorkflowType.SYSTEM_ORCHESTRATION
    return WorkflowType.CONTENT_GENERATION
