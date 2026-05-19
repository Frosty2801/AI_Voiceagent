import { Send } from 'lucide-react'

export function ChatComposer({ value, onChange, onSubmit, disabled }) {
  return (
    <form className="composer" onSubmit={onSubmit}>
      <input
        aria-label="Message"
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Ask about budgeting, savings, or currency conversion..."
        value={value}
      />
      <button disabled={disabled || !value.trim()} type="submit">
        <Send size={18} />
        Send
      </button>
    </form>
  )
}
