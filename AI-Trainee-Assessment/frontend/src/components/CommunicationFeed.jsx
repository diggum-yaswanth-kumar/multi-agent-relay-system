import { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble.jsx'

const AGENT_ROLES = {
  'Main Agent': 'Orchestrator',
  'Frontend Agent': 'Integration Agent',
  'Backend Agent': 'API & Content Engine',
}

export default function CommunicationFeed({ messages, typingAgent }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, typingAgent])

  return (
    <div className="panel communication-feed-panel">
      <div className="communication-feed__header">
        <h3 className="panel-title">Live Workflow Communication</h3>
        <span className="live-badge">
          <span className="live-dot" /> Live
        </span>
      </div>
      <div className="communication-feed">
        {messages.length === 0 && !typingAgent && (
          <div className="chat-empty chat-empty--compact">
            <div className="chat-empty__icon">◇</div>
            <h2>AI Orchestration Dashboard</h2>
            <p>
              Submit a task to watch agents collaborate in real time.
              <br />
              Try: <em>&quot;Build a blog generation system&quot;</em>
            </p>
          </div>
        )}
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {typingAgent && (
          <MessageBubble
            message={{
              role: 'agent',
              agent: typingAgent,
              agentRole: AGENT_ROLES[typingAgent] || 'Agent',
              isTyping: true,
            }}
          />
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
