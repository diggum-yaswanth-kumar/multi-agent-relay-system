const TONE_OPTIONS = ['Formal', 'Casual', 'Professional']
const LENGTH_OPTIONS = ['Short', 'Medium', 'Long']

export default function InputArea({
  onSubmit,
  disabled,
  clarificationField,
  placeholder,
}) {
  const isTone = clarificationField === 'tone'
  const isLength = clarificationField === 'length'
  const showQuickReplies = isTone || isLength

  const handleQuickReply = (value) => {
    if (!disabled) onSubmit(value)
  }

  const handleFormSubmit = (e) => {
    e.preventDefault()
    const input = e.target.elements.message
    const value = input.value.trim()
    if (value && !disabled) {
      onSubmit(value)
      input.value = ''
    }
  }

  return (
    <div className="input-area">
      {showQuickReplies && (
        <div className="quick-replies">
          <span className="quick-replies__label">Quick select:</span>
          <div className="quick-replies__buttons">
            {(isTone ? TONE_OPTIONS : LENGTH_OPTIONS).map((opt) => (
              <button
                key={opt}
                type="button"
                className="quick-reply-btn"
                onClick={() => handleQuickReply(opt)}
                disabled={disabled}
              >
                {opt}
              </button>
            ))}
          </div>
        </div>
      )}
      <form className="input-form" onSubmit={handleFormSubmit}>
        <input
          name="message"
          type="text"
          className="input-field"
          placeholder={placeholder || 'Describe the content you want to generate...'}
          disabled={disabled}
          autoComplete="off"
        />
        <button type="submit" className="send-btn" disabled={disabled}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
          </svg>
        </button>
      </form>
    </div>
  )
}
