export function getSessionId() {
  const key = 'finance_voiceagent_session'
  const existing = window.localStorage.getItem(key)
  if (existing) return existing

  const sessionId = crypto.randomUUID()
  window.localStorage.setItem(key, sessionId)
  return sessionId
}
