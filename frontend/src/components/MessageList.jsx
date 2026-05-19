import { Calculator, CircleDollarSign } from 'lucide-react'

const toolIcons = {
  safe_calculator: Calculator,
  currency_converter: CircleDollarSign,
}

export function MessageList({ messages, loading }) {
  return (
    <section className="messages" aria-live="polite">
      {messages.map((message) => (
        <article className={`message ${message.role}`} key={message.id}>
          <div className="message-header">
            <span>{message.role === 'user' ? 'You' : 'Finance VoiceAgent'}</span>
            {message.toolName ? <ToolBadge name={message.toolName} /> : null}
          </div>
          <p>{message.content}</p>
          {message.audioUrl ? (
            <audio controls src={message.audioUrl}>
              Your browser does not support audio playback.
            </audio>
          ) : null}
        </article>
      ))}
      {loading ? (
        <article className="message assistant loading">
          <div className="message-header">
            <span>Finance VoiceAgent</span>
          </div>
          <p>Thinking...</p>
        </article>
      ) : null}
    </section>
  )
}

function ToolBadge({ name }) {
  const Icon = toolIcons[name] || CircleDollarSign
  return (
    <span className="tool-badge">
      <Icon size={14} />
      {name}
    </span>
  )
}
