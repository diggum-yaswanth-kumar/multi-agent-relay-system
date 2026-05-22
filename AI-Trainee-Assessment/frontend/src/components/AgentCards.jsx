const AGENTS = [
  { id: 'main', name: 'Main Agent', role: 'Orchestrator', glow: 'glow-main' },
  { id: 'frontend', name: 'Frontend Agent', role: 'Integration', glow: 'glow-frontend' },
  { id: 'backend', name: 'Backend Agent', role: 'API & Content', glow: 'glow-backend' },
]

const AGENT_KEY = {
  'Main Agent': 'main',
  'Frontend Agent': 'frontend',
  'Backend Agent': 'backend',
}

export default function AgentCards({ activeAgent, typingAgent, agentStates }) {
  return (
    <div className="panel agent-cards-panel">
      <h3 className="panel-title">Agent Network</h3>
      <div className="agent-cards">
        {AGENTS.map((agent) => {
          const isTyping = typingAgent === agent.name
          const isActive =
            isTyping ||
            activeAgent === agent.name ||
            agentStates?.[agent.id] === 'active'
          return (
            <div
              key={agent.id}
              className={`agent-card ${agent.glow} ${isActive ? 'agent-card--active' : ''} ${isTyping ? 'agent-card--typing' : ''}`}
            >
              <div className="agent-card__indicator">
                <span className={`pulse ${isActive ? 'pulse--on' : ''}`} />
              </div>
              <div className="agent-card__info">
                <span className="agent-card__name">{agent.name}</span>
                <span className="agent-card__role">{agent.role}</span>
              </div>
              <span className={`agent-card__status ${isActive ? 'status--live' : ''}`}>
                {isTyping ? 'Typing...' : isActive ? 'Active' : 'Standby'}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export { AGENT_KEY }
