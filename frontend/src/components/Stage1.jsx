import { useMemo, useState } from 'react'
import ReactMarkdown from 'react-markdown'

export default function Stage1({ responses = [] }) {
  const [tab, setTab] = useState(0)

  const safeResponses = useMemo(() => responses.filter(Boolean), [responses])

  if (!safeResponses.length) return <p>No stage 1 responses yet.</p>

  const current = safeResponses[Math.min(tab, safeResponses.length - 1)]

  return (
    <div>
      <div className="tabs">
        {safeResponses.map((item, index) => (
          <button
            key={item.model}
            type="button"
            className={index === tab ? 'active' : ''}
            onClick={() => setTab(index)}
          >
            {item.model}
          </button>
        ))}
      </div>
      <div className="markdown-content panel">
        <ReactMarkdown>{current.content || ''}</ReactMarkdown>
      </div>
    </div>
  )
}
