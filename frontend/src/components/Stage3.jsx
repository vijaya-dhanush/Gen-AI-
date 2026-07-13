import ReactMarkdown from 'react-markdown'

export default function Stage3({ finalAnswer }) {
  if (!finalAnswer) return <p>No final synthesis yet.</p>

  return (
    <div className="markdown-content panel stage3-final">
      <ReactMarkdown>{finalAnswer}</ReactMarkdown>
    </div>
  )
}
