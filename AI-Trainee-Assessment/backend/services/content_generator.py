"""Content generation service — produces contextual AI-style output."""

from typing import Dict, Any


class ContentGenerator:
    """Generates final content based on task parameters and collected clarifications."""

    TONE_INTROS = {
        "formal": (
            "In accordance with contemporary industry discourse, the following "
            "analysis presents a structured examination of the subject matter."
        ),
        "casual": (
            "Hey there! So you wanted the scoop on this topic — let's dive in "
            "and keep things real and easy to follow."
        ),
        "professional": (
            "This enterprise-grade overview delivers actionable insights aligned "
            "with organizational standards and strategic communication objectives."
        ),
    }

    TONE_BODY_STYLES = {
        "formal": (
            "The implications thereof warrant careful consideration by stakeholders "
            "across relevant domains. Empirical evidence suggests sustained adoption "
            "of such methodologies yields measurable operational improvements."
        ),
        "casual": (
            "Honestly, it's pretty wild how fast things are moving. You've got teams "
            "trying new stuff every week, and the cool part is you don't need to be "
            "a tech wizard to get value out of it."
        ),
        "professional": (
            "Cross-functional teams benefit from standardized workflows, clear KPIs, "
            "and governance frameworks that ensure scalability, compliance, and "
            "repeatable outcomes across the organization."
        ),
    }

    LENGTH_SECTIONS = {
        "short": 1,
        "medium": 2,
        "long": 3,
    }

    def generate(self, task_context: Dict[str, Any]) -> str:
        """
        Generate contextual content from analyzed task and user parameters.

        Args:
            task_context: Contains topic, task_type, tone, length, original_request
        """
        topic = task_context.get("topic", "the requested subject")
        task_type = task_context.get("task_type", "content")
        tone = task_context.get("tone", "professional").lower()
        length = task_context.get("length", "medium").lower()
        original = task_context.get("original_request", "")

        if tone not in self.TONE_INTROS:
            tone = "professional"
        if length not in self.LENGTH_SECTIONS:
            length = "medium"

        intro = self.TONE_INTROS[tone]
        body_style = self.TONE_BODY_STYLES[tone]
        section_count = self.LENGTH_SECTIONS[length]

        title = self._build_title(task_type, topic)
        sections = self._build_sections(topic, task_type, body_style, section_count)
        conclusion = self._build_conclusion(tone, topic)
        meta = self._build_metadata(original, tone, length)

        parts = [
            f"# {title}",
            "",
            intro,
            "",
        ]
        parts.extend(sections)
        parts.extend(["", conclusion, "", "---", meta])

        return "\n".join(parts)

    def _build_title(self, task_type: str, topic: str) -> str:
        type_labels = {
            "blog": "Blog",
            "article": "Article",
            "summary": "Executive Summary",
            "email": "Email Draft",
            "report": "Report",
            "content": "Content Piece",
        }
        label = type_labels.get(task_type, "Content")
        return f"{label}: {topic.title()}"

    def _build_sections(self, topic: str, task_type: str, body_style: str, count: int) -> list:
        section_templates = [
            (
                f"## Understanding {topic.title()}\n\n"
                f"{topic.title()} represents a pivotal area of focus for modern organizations. "
                f"{body_style}"
            ),
            (
                f"## Key Developments & Applications\n\n"
                f"Organizations leveraging {topic} are seeing transformative results in efficiency, "
                f"decision-making, and competitive positioning. Integration strategies vary by "
                f"industry, but the core principles remain universally applicable."
            ),
            (
                f"## Strategic Recommendations\n\n"
                f"For teams implementing {topic}-related initiatives, we recommend phased rollouts, "
                f"pilot programs with measurable success criteria, and continuous feedback loops. "
                f"This {task_type} framework ensures alignment between technical capabilities and "
                f"business objectives."
            ),
        ]
        result = []
        for i in range(min(count, len(section_templates))):
            result.append(section_templates[i])
            result.append("")
        return result

    def _build_conclusion(self, tone: str, topic: str) -> str:
        conclusions = {
            "formal": (
                f"## Conclusion\n\n"
                f"In summation, {topic} constitutes a matter of substantive importance "
                f"requiring deliberate strategic engagement from all concerned parties."
            ),
            "casual": (
                f"## Wrapping Up\n\n"
                f"That's the gist on {topic}! Hope this helps you nail whatever you're working on."
            ),
            "professional": (
                f"## Conclusion\n\n"
                f"{topic.title()} remains a strategic priority. Teams that invest in structured "
                f"implementation will capture sustainable value and maintain competitive advantage."
            ),
        }
        return conclusions.get(tone, conclusions["professional"])

    def _build_metadata(self, original: str, tone: str, length: str) -> str:
        return (
            f"*Generated by Backend Agent | Tone: {tone.title()} | "
            f"Length: {length.title()} | Source request: \"{original[:80]}"
            f"{'...' if len(original) > 80 else ''}\"*"
        )
