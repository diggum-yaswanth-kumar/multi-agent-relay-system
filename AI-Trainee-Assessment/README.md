# AI Conversational Multi-Agent Relay System

**Real-Time Multi-Agent Workflow Orchestration Platform powered by GPT-4o-mini**

A production-style conversational AI platform where specialized agents collaborate through a **visible relay architecture**. Users watch Main, Frontend, and Backend agents communicate in a shared live chat while GPT-4o-mini generates the final content.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Features](#2-features)
3. [Architecture](#3-architecture)
4. [Agent Workflow](#4-agent-workflow)
5. [Tech Stack](#5-tech-stack)
6. [Project Structure](#6-project-structure)
7. [Installation Guide](#7-installation-guide)
8. [Environment Variables](#8-environment-variables)
9. [Running the Project](#9-running-the-project)
10. [Multi-Agent Relay Flow](#10-multi-agent-relay-flow)
11. [Screenshots](#11-screenshots)
12. [Future Improvements](#12-future-improvements)
13. [Author](#13-author)

---

## 1. Project Overview

This project is a **conversational multi-agent orchestration platform** that demonstrates how autonomous agents coordinate through strict relay messaging—not hidden pipelines or dashboard widgets.

**What it does:**

- Presents a **live multi-agent chat room** where User, Main Agent, Frontend Agent, and Backend Agent converse sequentially
- Runs a **multi-step clarification workflow** (tone → length) before generating content
- Delegates final content creation to **OpenAI GPT-4o-mini** via a dedicated `LLMService`
- Streams every relay step to the UI with typing animations and per-agent visual identity

**Why it matters:**

The system models how enterprise AI workflows can remain **transparent and auditable**: users see exactly which agent spoke, what was relayed, and when the LLM produced the final output.

---

## 2. Features

| Category | Capability |
|----------|------------|
| **Communication** | Real-time visible agent-to-agent relay in a single chat window |
| **Architecture** | Conversational relay: Main → Frontend → Backend → LLM → return path |
| **AI Generation** | GPT-4o-mini integration with structured prompts (topic, tone, length) |
| **Orchestration** | Main Agent controls workflow and user-facing clarification |
| **Clarifications** | Tone selection (Formal, Casual, Professional) |
| **Clarifications** | Length selection (Short, Medium, Long) |
| **UX** | Sequential message rendering with ~1s delays and typing indicators |
| **UI** | Dark futuristic theme, neon glow bubbles, agent avatars |
| **Backend** | FastAPI REST API with session-based workflow state |
| **Frontend** | React 18 + Vite SPA with API proxy and 90s LLM timeout |
| **Reliability** | API error handling, timeout handling, graceful LLM failure messages |

---

## 3. Architecture

### System Flow

```
User
  ↓
Main Agent          (Orchestrator — user interaction & workflow control)
  ↓
Frontend Agent      (Relay mediator — never talks to user directly)
  ↓
Backend Agent       (Content processing & parameter validation)
  ↓
GPT-4o-mini         (OpenAI — final content generation)
  ↓
Backend Agent
  ↓
Frontend Agent
  ↓
Main Agent
  ↓
User
```

### High-Level Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     React Frontend (Vite)                        │
│  ChatWindow · MessageBubble · InputArea · Sequential Relay UI   │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP JSON  /api/agent/*
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend (main.py)                   │
│  ┌─────────────────┐    ┌──────────────────┐                    │
│  │ OrchestratorAgent│───▶│  FrontendAgent   │                    │
│  │   (Main Agent)   │    │ (Relay Mediator) │                    │
│  └────────┬─────────┘    └────────┬─────────┘                    │
│           │                         │                              │
│  ┌────────▼─────────┐    ┌────────▼─────────┐                    │
│  │ WorkflowManager  │    │   BackendAgent   │                    │
│  │ RelayManager     │    │   TaskManager    │                    │
│  └──────────────────┘    └────────┬─────────┘                    │
│                                   │                              │
│                          ┌────────▼─────────┐                    │
│                          │    LLMService    │                    │
│                          │  (gpt-4o-mini)   │                    │
│                          └──────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Responsibilities

#### Main Agent (`orchestrator_agent.py`)

- Receives user requests and clarification answers
- Initiates and coordinates the relay workflow
- Speaks to the user (clarification questions, final delivery, errors)
- Communicates **only** with the User and Frontend Agent
- Never calls the LLM directly

#### Frontend Agent (`frontend_agent.py`)

- Acts exclusively as a **relay mediator**
- Forwards content requests and clarifications to the Backend Agent
- Packages Backend responses for the Main Agent
- Never communicates directly with the User

#### Backend Agent (`backend_agent.py`)

- Analyzes user requests (task type, topic extraction)
- Manages clarification state (tone, length)
- Invokes `LLMService.generate_content()` when all parameters are collected
- Returns structured relay payloads for the conversation chain

#### LLM Service (`services/llm_service.py`)

- Loads `OPENAI_API_KEY` from `.env`
- Builds structured prompts from topic, tone, length, and task type
- Calls OpenAI **GPT-4o-mini** with timeout and comprehensive error handling

---

## 4. Agent Workflow

### Phase 1 — Start Request

1. User submits a content request (e.g. blog about AI in hiring)
2. Main Agent acknowledges and delegates to Frontend Agent
3. Frontend Agent relays to Backend Agent
4. Backend Agent requests **tone** clarification via relay chain
5. Main Agent asks the user: *"What tone would you like?"*

### Phase 2 — Tone Clarification

1. User selects tone (Formal / Casual / Professional)
2. Relay chain forwards selection to Backend Agent
3. Backend Agent requests **length** clarification
4. Main Agent asks: *"What content length would you like?"*

### Phase 3 — Generation & Delivery

1. User selects length (Short / Medium / Long)
2. Relay chain triggers GPT-4o-mini generation
3. Backend Agent reports completion through Frontend → Main
4. Main Agent delivers generated content in chat bubbles

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Service metadata and architecture summary |
| `GET` | `/api/health` | Health check + `llm_configured` status |
| `POST` | `/api/agent/start` | Start workflow with user message |
| `POST` | `/api/agent/respond` | Submit clarification (`session_id`, `field`, `value`) |

Interactive API docs: **http://127.0.0.1:8000/docs**

---

## 5. Tech Stack

### Backend

| Technology | Role |
|------------|------|
| **Python 3.10+** | Runtime |
| **FastAPI** | REST API framework |
| **Uvicorn** | ASGI server |
| **Pydantic** | Request/response validation |
| **OpenAI SDK** | GPT-4o-mini integration |
| **python-dotenv** | Environment variable loading |

### Frontend

| Technology | Role |
|------------|------|
| **React 18** | UI framework |
| **Vite 6** | Dev server & build tool |
| **CSS3** | Dark neon chat styling |

### AI

| Model | Usage |
|-------|-------|
| **gpt-4o-mini** | Final content generation after clarifications |

---

## 6. Project Structure

```
AI-Trainee-Assessment/
│
├── backend/
│   ├── main.py                      # FastAPI app, routes, CORS, agent wiring
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Environment template (copy to .env)
│   ├── agents/
│   │   ├── orchestrator_agent.py    # Main Agent — orchestration & user relay
│   │   ├── frontend_agent.py        # Frontend Agent — relay mediator
│   │   ├── backend_agent.py         # Backend Agent — analysis & LLM trigger
│   │   ├── relay_manager.py         # Sequential relay message chains
│   │   ├── workflow_manager.py      # Session phase & conversation history
│   │   └── task_manager.py          # Parameter collection & task context
│   ├── models/
│   │   └── request_models.py        # Pydantic schemas (StartTask, Respond, AgentResponse)
│   └── services/
│       └── llm_service.py           # OpenAI GPT-4o-mini integration
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js               # Dev server + /api proxy to :8000
│   ├── index.html
│   └── src/
│       ├── App.jsx                  # Relay playback, state, API orchestration
│       ├── main.jsx
│       ├── components/
│       │   ├── ChatWindow.jsx       # Single shared chat area
│       │   ├── MessageBubble.jsx    # Agent bubbles, avatars, typing state
│       │   └── InputArea.jsx        # Input + quick-reply buttons
│       ├── services/
│       │   └── api.js               # API client with LLM timeout
│       └── styles/
│           └── app.css              # Dark futuristic neon theme
│
├── .gitignore                       # Excludes .env, node_modules, dist
└── README.md
```

---

## 7. Installation Guide

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** and **npm**
- **OpenAI API key** with access to `gpt-4o-mini`

### Backend

```bash
cd backend
pip install -r requirements.txt
```

Copy the environment template and add your API key (see [Environment Variables](#8-environment-variables)):

```bash
cp .env.example .env
```

### Frontend

```bash
cd frontend
npm install
```

---

## 8. Environment Variables

Create `backend/.env` from the template:

```bash
cd backend
cp .env.example .env
```

Required variable:

```env
OPENAI_API_KEY=your_api_key_here
```

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for GPT-4o-mini content generation |

**Security notes:**

- **Never** commit `.env` or API keys to GitHub
- `.env` is listed in `.gitignore` at the project root
- Use `.env.example` as the only committed template (no real keys)
- Rotate keys immediately if accidentally exposed

Optional frontend override:

```env
VITE_API_URL=http://127.0.0.1:8000
```

By default, Vite proxies `/api` to the backend during development.

---

## 9. Running the Project

Run **both** servers in separate terminals.

### Terminal 1 — Backend

```bash
cd backend
python -m uvicorn main:app --reload
```

- API: **http://127.0.0.1:8000**
- Docs: **http://127.0.0.1:8000/docs**
- Health: **http://127.0.0.1:8000/api/health** → confirm `"llm_configured": true`

### Terminal 2 — Frontend

```bash
cd frontend
npm run dev
```

- UI: **http://localhost:5173**

### Quick Test

1. Open the frontend in your browser
2. Send: `Create a short blog about AI in hiring`
3. Watch agents relay messages in the chat
4. Answer tone and length when Main Agent asks
5. Receive GPT-4o-mini generated content in the chat

### Production Build (Frontend)

```bash
cd frontend
npm run build
npm run preview
```

---

## 10. Multi-Agent Relay Flow

Every orchestration step is returned as `relay_messages` and played sequentially in the UI. Users see agents **talking to each other**—not system logs or hidden orchestration panels.

### Example Conversation

```
[User]
Create a short blog about AI in hiring

[Main Agent]
Task received. Frontend Agent, coordinate with Backend Agent.

[Frontend Agent]
Backend Agent, content generation request initiated.
Do you require clarification?

[Backend Agent]
Please ask the user what tone they prefer:
- Formal
- Casual
- Professional

[Frontend Agent]
Main Agent, Backend Agent requires tone clarification.

[Main Agent]
What tone would you like?

[User]
Formal

[Main Agent]
Frontend Agent, user selected Formal tone.

[Frontend Agent]
Backend Agent, tone received: Formal.
Do you require additional clarification?

[Backend Agent]
Please ask the user what content length they prefer:
- Short
- Medium
- Long

[Frontend Agent]
Main Agent, Backend Agent requires length clarification.

[Main Agent]
What content length would you like?

[User]
Medium

[Main Agent]
Frontend Agent, user selected Medium length.

[Frontend Agent]
Backend Agent, all required parameters collected. Generate final content.

[Backend Agent]
Generating final content...

[Backend Agent]
Content generation completed successfully.

[Frontend Agent]
Main Agent, backend processing completed successfully.

[Main Agent]
Here is your generated blog.

[Main Agent]
<GPT-4o-mini generated blog content>
```

### UI Experience

- **Single chat window** — all participants share one conversation thread
- **Agent avatars & neon bubbles** — purple (Main), blue (Frontend), cyan (Backend), neutral (User)
- **Typing animations** — each agent message is preceded by a typing indicator
- **Sequential delays** — messages appear one-by-one for a live collaborative feel
- **Quick-reply buttons** — tone and length options during clarification steps

---

## 11. Screenshots

> Add screenshots to a `docs/screenshots/` folder and reference them here for your portfolio.

| View | Description | Placeholder |
|------|-------------|-------------|
| Live Chat | Multi-agent relay conversation | `docs/screenshots/live-chat.png` |
| Clarification | Tone/length quick-reply UI | `docs/screenshots/clarification.png` |
| Generated Output | Final GPT-4o-mini blog delivery | `docs/screenshots/generated-content.png` |
| API Docs | FastAPI Swagger at `/docs` | `docs/screenshots/api-docs.png` |

**Suggested capture flow:** run a full blog request → screenshot relay messages → screenshot final content bubble.

---

## 12. Future Improvements

- **Conversation memory** — persist sessions and context across requests
- **Multi-user chat rooms** — shared agent channels with participant roles
- **Voice interaction** — speech-to-text input and text-to-speech agent replies
- **Streaming responses** — token-by-token LLM output in the chat bubble
- **Multiple LLM providers** — Anthropic, Gemini, local models via provider abstraction
- **Vector database integration** — RAG for topic-aware, document-grounded generation
- **Agent tool use** — web search, file upload, and structured output schemas
- **Authentication** — user accounts and API key management per tenant
- **Observability** — OpenTelemetry tracing across relay hops

---

## 13. Author

**AI Trainee Assessment Project**

Built as a portfolio-grade demonstration of:

- Multi-agent system design
- Relay-based orchestration patterns
- LLM integration best practices
- Full-stack FastAPI + React architecture

---

## License

This project was developed as an AI trainee assessment. Add your preferred license (e.g. MIT) before public distribution.

---

<p align="center">
  <strong>AI Conversational Multi-Agent Relay System</strong><br>
  Transparent agent collaboration · GPT-4o-mini powered · Production-style documentation
</p>
