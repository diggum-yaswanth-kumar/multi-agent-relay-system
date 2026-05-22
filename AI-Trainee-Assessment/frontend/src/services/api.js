const API_BASE = import.meta.env.VITE_API_URL || 'https://multi-agent-relay-system.onrender.com'
const LLM_TIMEOUT_MS = 90000

async function request(endpoint, options = {}) {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), LLM_TIMEOUT_MS)

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
      signal: controller.signal,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }))
      throw new Error(error.detail || error.message || `HTTP ${response.status}`)
    }

    return response.json()
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new Error(
        'Request timed out. GPT-4o-mini generation can take up to a minute — please try again.'
      )
    }
    throw err
  } finally {
    clearTimeout(timeoutId)
  }
}

export async function startWorkflow(message) {
  return request('/api/agent/start', {
    method: 'POST',
    body: JSON.stringify({ message }),
  })
}

export async function respondToClarification(sessionId, field, value) {
  return request('/api/agent/respond', {
    method: 'POST',
    body: JSON.stringify({
      session_id: sessionId,
      field,
      value,
    }),
  })
}

export async function healthCheck() {
  return request('/api/health')
}
