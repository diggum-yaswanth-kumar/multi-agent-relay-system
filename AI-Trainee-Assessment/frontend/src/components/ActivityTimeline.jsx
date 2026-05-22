const AGENT_CLASS = {
  'Main Agent': 'timeline-item--main',
  'Frontend Agent': 'timeline-item--frontend',
  'Backend Agent': 'timeline-item--backend',
  User: 'timeline-item--user',
}

export default function ActivityTimeline({ logs, typingAgent }) {
  const items = logs || []

  return (
    <div className="panel timeline-panel">
      <h3 className="panel-title">Activity Timeline</h3>
      <div className="timeline">
        {items.length === 0 && !typingAgent && (
          <p className="timeline-empty">Workflow events will appear here.</p>
        )}
        {items.map((entry, idx) => (
          <div
            key={`${entry.agent}-${idx}-${entry.workflow_step || idx}`}
            className={`timeline-item ${AGENT_CLASS[entry.agent] || ''}`}
          >
            <div className="timeline-item__dot" />
            <div className="timeline-item__content">
              <span className="timeline-item__agent">{entry.agent}</span>
              {entry.workflow_step != null && (
                <span className="timeline-item__step">Step {entry.workflow_step}</span>
              )}
              <p className="timeline-item__message">
                {(entry.message || '').split('\n')[0]}
              </p>
              {entry.status && (
                <span className={`timeline-item__status status-${entry.status}`}>
                  {entry.status}
                </span>
              )}
            </div>
          </div>
        ))}
        {typingAgent && (
          <div className={`timeline-item timeline-item--typing ${AGENT_CLASS[typingAgent] || ''}`}>
            <div className="timeline-item__dot timeline-item__dot--pulse" />
            <div className="timeline-item__content">
              <span className="timeline-item__agent">{typingAgent}</span>
              <p className="timeline-item__message">Processing...</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
