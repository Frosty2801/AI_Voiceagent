export function ModeToggle({ mode, onChange }) {
  return (
    <div className="mode-toggle" aria-label="Response mode">
      <button
        className={mode === 'text' ? 'active' : ''}
        type="button"
        onClick={() => onChange('text')}
      >
        Text
      </button>
      <button
        className={mode === 'voice' ? 'active' : ''}
        type="button"
        onClick={() => onChange('voice')}
      >
        Voice
      </button>
    </div>
  )
}
