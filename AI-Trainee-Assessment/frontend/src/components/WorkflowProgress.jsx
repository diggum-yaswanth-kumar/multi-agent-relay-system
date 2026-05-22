export default function WorkflowProgress({ steps, phase, workflowType }) {
  if (!steps?.length) return null

  const completed = steps.filter((s) => s.status === 'completed').length
  const progress = Math.round((completed / steps.length) * 100)

  return (
    <div className="panel workflow-progress-panel">
      <div className="workflow-progress__header">
        <h3 className="panel-title">Workflow Progress</h3>
        <span className="workflow-progress__pct">{progress}%</span>
      </div>
      {workflowType && (
        <span className="workflow-type-badge">
          {workflowType === 'system_orchestration' ? 'System Build' : 'Content Gen'}
        </span>
      )}
      <div className="workflow-progress__bar">
        <div className="workflow-progress__fill" style={{ width: `${progress}%` }} />
      </div>
      <ol className="workflow-steps">
        {steps.map((step) => (
          <li
            key={step.id}
            className={
              step.status === 'completed'
                ? 'step--done'
                : step.status === 'active'
                  ? 'step--current'
                  : ''
            }
          >
            {step.label}
          </li>
        ))}
      </ol>
      {phase && <p className="workflow-phase">Phase: {phase.replace(/_/g, ' ')}</p>}
    </div>
  )
}
