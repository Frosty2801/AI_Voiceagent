export function speakWithBrowser(text) {
  if (!('speechSynthesis' in window)) return false

  window.speechSynthesis.cancel()
  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = 'en-US'
  utterance.rate = 0.95
  window.speechSynthesis.speak(utterance)
  return true
}
