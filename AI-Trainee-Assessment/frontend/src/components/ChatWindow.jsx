import { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble.jsx'

const AGENT_ROLES = {
  'Main Agent': 'Lead Coordinator',
  'Frontend Agent': 'Communication Bridge',
  'Backend Agent': 'Content Engine',
}

export default function ChatWindow({ messages, typingAgent }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, typingAgent])

  return (
    <div className="chat-window">
      {messages.length === 0 && !typingAgent && (
        <div className="chat-empty">
          <div className="chat-empty__icon">◇</div>
          <h2>Live Agent Chat</h2>
          <p>
            Four participants — you and three AI agents — share one conversation.
            <br />
            Try: <em>&quot;Create a short blog about AI in hiring&quot;</em>
          </p>
          <div className="chat-participants">
            <span className="participant participant--main">Main</span>
            <span className="participant participant--frontend">Frontend</span>
            <span className="participant participant--backend">Backend</span>
            <span className="participant participant--user">You</span>
          </div>
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
  )
}
