# AI Conversational Multi-Agent Relay System

### Real-Time GPT-4o-mini Powered Multi-Agent Orchestration Platform

A futuristic AI-powered conversational workflow system where multiple specialized agents communicate visibly in real time through a relay-based orchestration architecture.

This project demonstrates a professional multi-agent communication pipeline using React, FastAPI, and OpenAI GPT-4o-mini.

---

# 🚀 Features

- 🤖 Real-time visible agent-to-agent communication
- 🧠 GPT-4o-mini powered intelligent response generation
- 🔄 Conversational relay workflow architecture
- 👨‍💼 Main Agent orchestration system
- 🌐 Frontend Agent communication mediator
- ⚙️ Backend Agent content processing
- 💬 Multi-step clarification workflow
- 🎨 Dark futuristic glowing UI
- ⚡ FastAPI backend + React frontend
- 🪄 Sequential live chat rendering
- ✨ Typing animations & live workflow feeling
- 📡 Real-time orchestration communication

---

# 🏗️ System Architecture

```text
User
↓
Main Agent
↓
Frontend Agent
↓
Backend Agent
↓
GPT-4o-mini
↓
Backend Agent
↓
Frontend Agent
↓
Main Agent
↓
User
```

---

# 🤖 Agent Responsibilities

## 🟣 Main Agent

- Receives user requests
- Controls workflow orchestration
- Requests clarification from user
- Delivers final response
- Coordinates relay communication

---

## 🔵 Frontend Agent

- Acts as communication mediator
- Relays messages between agents
- Maintains visible conversation flow
- Coordinates workflow updates

---

## 🟢 Backend Agent

- Handles processing logic
- Integrates with GPT-4o-mini
- Requests clarification requirements
- Generates intelligent content responses

---

# 🔄 Relay Workflow Example

```text
[User]
Create a blog about AI in hiring

[Main Agent]
Task received.
Frontend Agent, coordinate with Backend Agent.

[Frontend Agent]
Backend Agent, content generation request initiated.

[Backend Agent]
Please ask the user what tone they prefer.

[Frontend Agent]
Main Agent, Backend Agent requires tone clarification.

[Main Agent]
What tone would you like?

[User]
Professional

[Backend Agent]
Please ask the user what content length they prefer.

[User]
Medium

[Backend Agent]
Generating final content using GPT-4o-mini...

[Main Agent]
Here is your generated blog.
```

---

# 🧠 GPT-4o-mini Integration

The Backend Agent integrates with OpenAI GPT-4o-mini to generate intelligent contextual responses based on:

- User topic/request
- Selected tone
- Selected content length

The LLM is used only for content generation while the multi-agent relay architecture handles orchestration and communication.

---

# 🎨 UI Highlights

- Futuristic dark theme
- Neon glowing effects
- Real-time live chat experience
- Animated agent communication
- Sequential workflow rendering
- Glassmorphism styling
- Smooth typing animations
- Modern SaaS AI dashboard feel

---

# 🛠️ Tech Stack

| Layer | Technologies |
|---|---|
| Frontend | React, Vite, Modern CSS |
| Backend | FastAPI, Python |
| AI/LLM | OpenAI GPT-4o-mini |
| Validation | Pydantic |
| API Server | Uvicorn |

---

# 📂 Project Structure

```text
AI-Trainee-Assessment/
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env
│   │
│   ├── agents/
│   │   ├── orchestrator_agent.py
│   │   ├── frontend_agent.py
│   │   ├── backend_agent.py
│   │   ├── workflow_manager.py
│   │   └── task_manager.py
│   │
│   ├── models/
│   │   └── request_models.py
│   │
│   └── services/
│       ├── llm_service.py
│       └── content_generator.py
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   │
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       │
│       ├── components/
│       │   ├── ChatWindow.jsx
│       │   ├── MessageBubble.jsx
│       │   ├── InputArea.jsx
│       │   └── AgentStatus.jsx
│       │
│       ├── services/
│       │   └── api.js
│       │
│       └── styles/
│           └── app.css
│
└── README.md
```

---

# ⚙️ Installation Guide

## 1️⃣ Clone Repository

```bash
git clone https://github.com/diggum-yaswanth-kumar/multi-agent-relay-system.git
```

---

# 🔧 Backend Setup

```bash
cd backend

pip install -r requirements.txt

python -m uvicorn main:app --reload
```

Backend runs on:

```text
http://127.0.0.1:8000
```

---

# 🌐 Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

Frontend runs on:

```text
http://localhost:5173
```

---

# 🔐 Environment Variables

Create a `.env` file inside the `backend` folder:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

---

# 🚨 Important Security Note

Never push your `.env` file to GitHub.

Make sure `.gitignore` contains:

```gitignore
.env
node_modules
__pycache__
dist
```

---

# ▶️ Running the Project

## Start Backend

```bash
cd backend
python -m uvicorn main:app --reload
```

---

## Start Frontend

```bash
cd frontend
npm run dev
```

---

# 🧪 Example Test Prompt

```text
Create a blog about AI in healthcare
```

The system will:

1. Initiate Main Agent orchestration
2. Relay communication through Frontend Agent
3. Request tone clarification
4. Request length clarification
5. Generate GPT-4o-mini response
6. Display final output in live chat

---

# 🔮 Future Improvements

- Memory support
- Streaming LLM responses
- Voice interaction
- Multi-user collaboration
- Vector database integration
- Multi-LLM provider support
- WebSocket real-time communication
- Agent memory persistence
- Autonomous task chaining

---

# 👨‍💻 Author

### Diggum Yaswanth Kumar

AI & ML Developer | Data Analyst | Python Developer

GitHub:
https://github.com/diggum-yaswanth-kumar

---

# 📄 License

This project was developed for AI multi-agent workflow orchestration demonstration and educational purposes.

---

# ⭐ Final Note

This project demonstrates a professional conversational relay-based multi-agent architecture where specialized AI agents collaborate visibly in real time while leveraging GPT-4o-mini for intelligent content generation.
