import { useState, useCallback } from 'react'
import ChatWindow from './components/ChatWindow.jsx'
import InputArea from './components/InputArea.jsx'
import { startWorkflow, respondToClarification } from './services/api.js'

let messageId = 0
const nextId = () => `msg-${++messageId}`

const TYPING_DELAY = 900
const MESSAGE_GAP = 1000

const delay = (ms) => new Promise((r) => setTimeout(r, ms))

const AGENT_ROLES = {
  'Main Agent': 'Lead Coordinator',
  'Frontend Agent': 'Communication Bridge',
  'Backend Agent': 'Content Engine',
  User: 'You',
}

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

  const addMessage = useCallback((msg) => {
    setMessages((prev) => [...prev, { id: nextId(), timestamp: formatTime(), ...msg }])
  }, [])

  const playRelayMessages = async (relayMessages) => {
    if (!relayMessages?.length) return

    for (const entry of relayMessages) {
      const agent = entry.agent || 'Main Agent'
      setTypingAgent(agent)
      await delay(TYPING_DELAY)

      setTypingAgent(null)
      addMessage({
        role: agent === 'User' ? 'user' : 'agent',
        agent,
        agentRole: AGENT_ROLES[agent] || 'Agent',
        content: entry.message,
      })
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
    const relay = data.relay_messages || data.orchestration_logs || []
    const lastRelay = relay[relay.length - 1]
    const deliveryIntro =
      data.status === 'completed' && lastRelay?.agent === 'Main Agent'
        ? lastRelay.message
        : null
    const relayToPlay =
      deliveryIntro && relay.length > 1 ? relay.slice(0, -1) : relay

    if (relayToPlay.length) {
      await playRelayMessages(relayToPlay)
    }

    if (data.status === 'needs_clarification') {
      setSessionId(data.session_id)
      setClarificationField(data.field)
    } else if (data.status === 'completed') {
      setClarificationField(null)
      setSessionId(null)
      await deliverGeneratedContent(deliveryIntro, data.result)
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
    }

    setIsProcessing(false)
    setTypingAgent(null)
  }

  const runWithAgents = async (apiCall) => {
    setIsProcessing(true)
    try {
      const data = await apiCall()
      await handleApiResponse(data)
    } catch (err) {
      setIsProcessing(false)
      setTypingAgent(null)
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

    if (sessionId && clarificationField) {
      runWithAgents(() =>
        respondToClarification(sessionId, clarificationField, text)
      )
    } else {
      runWithAgents(() => startWorkflow(text))
    }
  }

  const inputPlaceholder = clarificationField
    ? clarificationField === 'tone'
      ? 'Reply with tone: Formal, Casual, or Professional'
      : 'Reply with length: Short, Medium, or Long'
    : 'Create a short blog about AI in hiring...'

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-header__brand">
          <span className="brand-icon">◈</span>
          <div>
            <h1>AI Agent Communication System</h1>
            <p>Live Multi-Agent Chat Room</p>
          </div>
        </div>
        <div className="app-header__badge">
          <span className="live-dot" />
          {typingAgent
            ? `${typingAgent} is typing...`
            : isProcessing
              ? 'GPT-4o-mini generating...'
              : 'Agents online'}
        </div>
      </header>

      <main className="app-main">
        <ChatWindow messages={messages} typingAgent={typingAgent} />
        <InputArea
          onSubmit={handleUserSubmit}
          disabled={isProcessing}
          clarificationField={clarificationField}
          placeholder={inputPlaceholder}
        />
      </main>
    </div>
  )
}
