const AGENT_CONFIG = {
  User: {
    badge: 'badge-user',
    bubble: 'user',
    role: 'You',
    avatar: 'U',
    iconClass: 'avatar-user',
  },
  'Main Agent': {
    badge: 'badge-main',
    bubble: 'main',
    role: 'Lead Coordinator',
    avatar: 'M',
    iconClass: 'avatar-main',
  },
  'Frontend Agent': {
    badge: 'badge-frontend',
    bubble: 'frontend',
    role: 'Communication Bridge',
    avatar: 'F',
    iconClass: 'avatar-frontend',
  },
  'Backend Agent': {
    badge: 'badge-backend',
    bubble: 'backend',
    role: 'Content Engine',
    avatar: 'B',
    iconClass: 'avatar-backend',
  },
}

export default function MessageBubble({ message }) {
  const {
    role,
    agent,
    agentRole,
    content,
    timestamp,
    isTyping,
    isLongForm,
  } = message

  const config = AGENT_CONFIG[agent] || {
    badge: '',
    bubble: 'agent',
    role: 'Agent',
    avatar: '?',
    iconClass: '',
  }
  const isUser = role === 'user' || agent === 'User'

  if (isTyping) {
    return (
      <div
        className={`message-row message-row--agent message-row--${config.bubble} message-row--typing`}
      >
        <div className="message-body">
          <div className={`agent-avatar ${config.iconClass}`}>{config.avatar}</div>
          <div className="message-content">
            <div className="message-header">
              <span className={`agent-badge ${config.badge}`}>{agent}</span>
              <span className="agent-role">{agentRole || config.role}</span>
            </div>
            <div
              className={`message-bubble message-bubble--typing message-bubble--${config.bubble}`}
            >
              <span className="typing-label">{agent} is typing</span>
              <span className="typing-dots">
                <span />
                <span />
                <span />
              </span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div
      className={`message-row message-row--${isUser ? 'user' : 'agent'} message-row--${config.bubble} ${isLongForm ? 'message-row--longform' : ''}`}
    >
      <div className="message-body">
        {!isUser && (
          <div className={`agent-avatar ${config.iconClass}`}>{config.avatar}</div>
        )}
        <div className="message-content">
          <div
            className={`message-header ${isUser ? 'message-header--user' : ''}`}
          >
            <span className={`agent-badge ${config.badge}`}>
              {isUser ? 'User' : agent}
            </span>
            <span className="agent-role">{agentRole || config.role}</span>
            {timestamp && <span className="message-time">{timestamp}</span>}
          </div>
          <div
            className={`message-bubble message-bubble--${config.bubble} ${isLongForm ? 'message-bubble--longform' : ''}`}
          >
            {isLongForm ? (
              <pre className="message-longform">{content}</pre>
            ) : (
              <p>{content}</p>
            )}
          </div>
        </div>
        {isUser && (
          <div className={`agent-avatar ${config.iconClass}`}>{config.avatar}</div>
        )}
      </div>
    </div>
  )
}
