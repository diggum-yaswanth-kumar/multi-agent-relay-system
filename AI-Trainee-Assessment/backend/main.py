"""
AI Agent Communication System — Conversational Multi-Agent Relay System
User → Main Agent → Frontend Agent → Backend Agent → Frontend Agent → Main Agent → User
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models.request_models import StartTaskRequest, RespondRequest, AgentResponse
from agents.task_manager import TaskManager
from agents.workflow_manager import WorkflowManager
from agents.backend_agent import BackendAgent
from agents.frontend_agent import FrontendAgent
from agents.orchestrator_agent import OrchestratorAgent
from services.llm_service import LLMService

app = FastAPI(
    title="AI Agent Communication System",
    description="Conversational multi-agent relay orchestration platform",
    version="4.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)

task_manager = TaskManager()
workflow_manager = WorkflowManager()
llm_service = LLMService()
backend_agent = BackendAgent(task_manager, llm_service)
frontend_agent = FrontendAgent(backend_agent)
orchestrator = OrchestratorAgent(workflow_manager, frontend_agent)


@app.get("/")
async def root():
    return {
        "service": "AI Agent Communication System",
        "status": "operational",
        "architecture": "Multi-Agent Workflow Orchestration",
        "flow": "User → Main → Frontend → Backend → [GPT-4o-mini] → Frontend → Main → User",
        "workflows": ["system_orchestration", "content_generation"],
        "agents": ["Main Agent", "Frontend Agent", "Backend Agent"],
        "endpoints": {
            "start": "POST /api/agent/start",
            "respond": "POST /api/agent/respond",
        },
    }


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "agents_online": True,
        "orchestrator": "Main Agent",
        "relay_active": True,
        "llm_model": "gpt-4o-mini",
        "llm_configured": llm_service.is_configured,
    }


@app.post("/api/agent/start", response_model=AgentResponse)
async def start_agent_workflow(request: StartTaskRequest):
    """Start relay workflow — Main Agent receives user request."""
    result = orchestrator.start_orchestration(request.message)
    return AgentResponse(**result)


@app.post("/api/agent/respond", response_model=AgentResponse)
async def respond_to_clarification(request: RespondRequest):
    """Submit clarification — relayed Main → Frontend → Backend."""
    if not task_manager.session_exists(request.session_id):
        raise HTTPException(status_code=404, detail="Session not found or expired.")

    result = orchestrator.process_clarification(
        request.session_id,
        request.field,
        request.value,
    )
    return AgentResponse(**result)
