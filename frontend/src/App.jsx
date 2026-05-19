import { useMemo, useState } from 'react'
import { Landmark } from 'lucide-react'
import { sendChatMessage } from './api/client.js'
import { ChatComposer } from './components/ChatComposer.jsx'
import { MessageList } from './components/MessageList.jsx'
import { ModeToggle } from './components/ModeToggle.jsx'
import { getSessionId } from './utils/session.js'
import { speakWithBrowser } from './utils/speech.js'

const examples = [
  'Convert 100 USD to EUR.',
  'If I save 250 every month for 12 months, how much will I save?',
  'What is a good way to organize my monthly budget?',
]

export function App() {
  const sessionId = useMemo(() => getSessionId(), [])
  const [mode, setMode] = useState('text')
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(event) {
    event.preventDefault()
    const text = input.trim()
    if (!text || loading) return

    setError('')
    setInput('')
    setLoading(true)
    setMessages((current) => [
      ...current,
      { id: crypto.randomUUID(), role: 'user', content: text },
    ])

    try {
      const response = await sendChatMessage({ session_id: sessionId, message: text, mode })
      if (response.mode === 'voice' && response.tts_failed) {
        speakWithBrowser(response.reply)
      }
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: response.reply,
          toolName: response.used_tool ? response.tool_name : null,
          audioUrl: response.audio_url,
        },
      ])
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="app-shell">
      <section className="topbar">
        <div className="brand">
          <span className="brand-icon">
            <Landmark size={24} />
          </span>
          <div>
            <h1>Finance VoiceAgent</h1>
            <p>Personal finance chat with tools for calculations and currency conversion.</p>
          </div>
        </div>
        <ModeToggle mode={mode} onChange={setMode} />
      </section>

      <MessageList messages={messages} loading={loading} />

      {error ? <p className="error">{error}</p> : null}

      <div className="examples">
        {examples.map((example) => (
          <button key={example} type="button" onClick={() => setInput(example)}>
            {example}
          </button>
        ))}
      </div>

      <ChatComposer
        disabled={loading}
        onChange={setInput}
        onSubmit={handleSubmit}
        value={input}
      />
    </main>
  )
}
