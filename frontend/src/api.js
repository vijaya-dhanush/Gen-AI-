const API_BASE = 'http://localhost:8001/api'

async function req(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || `Request failed with status ${response.status}`)
  }

  return response.json()
}

export const api = {
  health: () => req('/health'),
  listConversations: () => req('/conversations'),
  createConversation: () => req('/conversations', { method: 'POST' }),
  getConversation: (id) => req(`/conversations/${id}`),
  sendMessage: (id, content) =>
    req(`/conversations/${id}/message`, {
      method: 'POST',
      body: JSON.stringify({ content }),
    }),
}
