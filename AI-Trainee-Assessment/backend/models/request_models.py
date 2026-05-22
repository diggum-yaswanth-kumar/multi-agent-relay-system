from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class StartTaskRequest(BaseModel):
    """Initial user content generation request."""
    message: str = Field(..., min_length=1, description="User's task or content request")


class RespondRequest(BaseModel):
    """Clarification response relayed through Main Agent orchestration."""
    session_id: str = Field(..., description="Active orchestration session identifier")
    field: str = Field(..., description="Field being clarified (tone, length)")
    value: str = Field(..., min_length=1, description="User's answer to clarification question")


class WorkflowMessage(BaseModel):
    """Structured multi-agent workflow communication message."""
    agent: str
    message: str
    status: str = "processing"
    workflow_step: int = 1
    direction: Optional[str] = "relay"


class OrchestrationLogEntry(BaseModel):
    agent: str
    message: str


class WorkflowStepStatus(BaseModel):
    id: str
    label: str
    status: str = "pending"


class AgentResponse(BaseModel):
    """Standard API response envelope with orchestration metadata."""
    status: str
    agent: str
    session_id: Optional[str] = None
    question: Optional[str] = None
    field: Optional[str] = None
    result: Optional[str] = None
    message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    main_agent: Optional[str] = None
    frontend_agent: Optional[str] = None
    routing_log: Optional[str] = None
    orchestration_logs: Optional[List[Dict[str, str]]] = None
    relay_messages: Optional[List[Dict[str, str]]] = None
    workflow_messages: Optional[List[Dict[str, Any]]] = None
    communication_logs: Optional[List[Dict[str, Any]]] = None
    conversation_history: Optional[List[Dict[str, str]]] = None
    orchestration_summary: Optional[str] = None
    workflow_phase: Optional[str] = None
    workflow_steps: Optional[List[Dict[str, Any]]] = None
