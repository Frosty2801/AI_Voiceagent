const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export async function sendChatMessage(payload) {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new Error(error.detail || 'The assistant is unavailable.')
  }

  const data = await response.json()
  return {
    ...data,
    audio_url: data.audio_url ? `${API_BASE_URL}${data.audio_url}` : null,
  }
}
