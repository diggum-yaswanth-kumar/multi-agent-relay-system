import { useState, useCallback } from 'react'
import CommunicationFeed from './components/CommunicationFeed.jsx'
import InputArea from './components/InputArea.jsx'
import AgentCards from './components/AgentCards.jsx'
import WorkflowProgress from './components/WorkflowProgress.jsx'
import ActivityTimeline from './components/ActivityTimeline.jsx'
import { startWorkflow, respondToClarification } from './services/api.js'

let messageId = 0
const nextId = () => `msg-${++messageId}`

const TYPING_DELAY = 900
const MESSAGE_GAP = 1000

const delay = (ms) => new Promise((r) => setTimeout(r, ms))

const AGENT_ROLES = {
  'Main Agent': 'Orchestrator',
  'Frontend Agent': 'Integration Agent',
  'Backend Agent': 'API & Content Engine',
  User: 'You',
}

const AGENT_STATE_MAP = {
  'Main Agent': 'main',
  'Frontend Agent': 'frontend',
  'Backend Agent': 'backend',
}

const DEFAULT_WORKFLOW_STEPS = []

function formatTime() {
  return new Date().toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

export default function App() {
  const [messages, setMessages] = useState([])
  const [sessionId, setSessionId] = useState(null)
  const [clarificationField, setClarificationField] = useState(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [typingAgent, setTypingAgent] = useState(null)
  const [activeAgent, setActiveAgent] = useState(null)
  const [workflowSteps, setWorkflowSteps] = useState(DEFAULT_WORKFLOW_STEPS)
  const [workflowPhase, setWorkflowPhase] = useState(null)
  const [workflowType, setWorkflowType] = useState(null)
  const [communicationLogs, setCommunicationLogs] = useState([])
  const [agentStates, setAgentStates] = useState({
    main: 'idle',
    frontend: 'idle',
    backend: 'idle',
  })

  const addMessage = useCallback((msg) => {
    setMessages((prev) => [...prev, { id: nextId(), timestamp: formatTime(), ...msg }])
  }, [])

  const setAgentFromName = (agentName, state) => {
    const key = AGENT_STATE_MAP[agentName]
    if (key) setAgentStates((prev) => ({ ...prev, [key]: state }))
  }

  const playWorkflowMessages = async (workflowMessages) => {
    if (!workflowMessages?.length) return

    for (const entry of workflowMessages) {
      const agent = entry.agent || 'Main Agent'
      setActiveAgent(agent)
      setTypingAgent(agent)
      setAgentFromName(agent, 'active')
      await delay(TYPING_DELAY)

      setTypingAgent(null)
      addMessage({
        role: agent === 'User' ? 'user' : 'agent',
        agent,
        agentRole: AGENT_ROLES[agent] || 'Agent',
        content: entry.message,
        workflowStep: entry.workflow_step,
        workflowStatus: entry.status,
      })
      setCommunicationLogs((prev) => [...prev, entry])
      await delay(MESSAGE_GAP)
    }
    setTypingAgent(null)
  }

  const deliverGeneratedContent = async (intro, content) => {
    if (intro) {
      setTypingAgent('Main Agent')
      await delay(TYPING_DELAY)
      setTypingAgent(null)
      addMessage({
        role: 'agent',
        agent: 'Main Agent',
        agentRole: AGENT_ROLES['Main Agent'],
        content: intro,
      })
      await delay(MESSAGE_GAP)
    }

    if (content) {
      setTypingAgent('Main Agent')
      await delay(TYPING_DELAY)
      setTypingAgent(null)
      addMessage({
        role: 'agent',
        agent: 'Main Agent',
        agentRole: AGENT_ROLES['Main Agent'],
        content,
        isLongForm: true,
      })
    }
  }

  const handleApiResponse = async (data) => {
    if (data.workflow_steps?.length) {
      setWorkflowSteps(data.workflow_steps)
    }
    if (data.workflow_phase) setWorkflowPhase(data.workflow_phase)
    if (data.metadata?.workflow_type) setWorkflowType(data.metadata.workflow_type)

    const workflowMsgs =
      data.workflow_messages ||
      (data.relay_messages || data.orchestration_logs || []).map((m, i) => ({
        ...m,
        status: data.status === 'completed' && i === (data.relay_messages?.length || 0) - 1
          ? 'completed'
          : 'processing',
        workflow_step: i + 1,
      }))

    if (workflowMsgs.length) {
      await playWorkflowMessages(workflowMsgs)
    }

    if (data.status === 'needs_clarification') {
      setSessionId(data.session_id)
      setClarificationField(data.field)
      setActiveAgent('Main Agent')
    } else if (data.status === 'completed') {
      setClarificationField(null)
      setSessionId(null)
      setActiveAgent('Main Agent')
      setAgentStates({ main: 'idle', frontend: 'idle', backend: 'idle' })

      if (data.result) {
        const showAsDeliverable =
          data.result.startsWith('#') || data.result.length > 120
        if (showAsDeliverable) {
          await deliverGeneratedContent(null, data.result)
        }
      }
    } else if (data.status === 'error') {
      setTypingAgent('Main Agent')
      await delay(TYPING_DELAY)
      setTypingAgent(null)
      addMessage({
        role: 'agent',
        agent: 'Main Agent',
        agentRole: AGENT_ROLES['Main Agent'],
        content: data.message || 'An error occurred.',
      })
      setAgentStates({ main: 'idle', frontend: 'idle', backend: 'idle' })
    }

    if (data.communication_logs?.length) {
      setCommunicationLogs(data.communication_logs)
    }

    setIsProcessing(false)
    setTypingAgent(null)
  }

  const runWithAgents = async (apiCall) => {
    setIsProcessing(true)
    setAgentStates({ main: 'active', frontend: 'active', backend: 'active' })
    try {
      const data = await apiCall()
      await handleApiResponse(data)
    } catch (err) {
      setIsProcessing(false)
      setTypingAgent(null)
      setAgentStates({ main: 'idle', frontend: 'idle', backend: 'idle' })
      addMessage({
        role: 'agent',
        agent: 'Main Agent',
        agentRole: AGENT_ROLES['Main Agent'],
        content: `Connection error: ${err.message}. Ensure the backend is running on port 8000.`,
      })
    }
  }

  const handleUserSubmit = (text) => {
    addMessage({
      role: 'user',
      agent: 'User',
      agentRole: AGENT_ROLES.User,
      content: text,
    })
    setCommunicationLogs((prev) => [
      ...prev,
      { agent: 'User', message: text, status: 'received', workflow_step: 0 },
    ])

    if (sessionId && clarificationField) {
      runWithAgents(() =>
        respondToClarification(sessionId, clarificationField, text)
      )
    } else {
      setCommunicationLogs([])
      setWorkflowSteps(DEFAULT_WORKFLOW_STEPS)
      runWithAgents(() => startWorkflow(text))
    }
  }

  const inputPlaceholder = clarificationField
    ? clarificationField === 'tone'
      ? 'Reply with tone: Formal, Casual, or Professional'
      : 'Reply with length: Short, Medium, or Long'
    : 'Build a blog generation system...'

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-header__brand">
          <span className="brand-icon">◈</span>
          <div>
            <h1>AI Multi-Agent Orchestration</h1>
            <p>Enterprise Workflow Collaboration Platform</p>
          </div>
        </div>
        <div className="app-header__badge">
          <span className="live-dot" />
          {typingAgent
            ? `${typingAgent} is typing...`
            : isProcessing
              ? 'Orchestrating workflow...'
              : 'All agents online'}
        </div>
      </header>

      <main className="dashboard">
        <aside className="dashboard-sidebar">
          <AgentCards
            activeAgent={activeAgent}
            typingAgent={typingAgent}
            agentStates={agentStates}
          />
          <WorkflowProgress
            steps={workflowSteps}
            phase={workflowPhase}
            workflowType={workflowType}
          />
        </aside>

        <section className="dashboard-main">
          <CommunicationFeed messages={messages} typingAgent={typingAgent} />
          <InputArea
            onSubmit={handleUserSubmit}
            disabled={isProcessing}
            clarificationField={clarificationField}
            placeholder={inputPlaceholder}
          />
        </section>

        <aside className="dashboard-aside">
          <ActivityTimeline logs={communicationLogs} typingAgent={typingAgent} />
        </aside>
      </main>
    </div>
  )
}
