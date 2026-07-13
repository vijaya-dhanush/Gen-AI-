import { useMemo, useState } from 'react'
import ReactMarkdown from 'react-markdown'

export default function Stage2({ rankings = [], metadata }) {
  const [tab, setTab] = useState(0)
  const safeRankings = useMemo(() => rankings.filter(Boolean), [rankings])

  if (!safeRankings.length) return <p>No stage 2 evaluations yet.</p>

  const current = safeRankings[Math.min(tab, safeRankings.length - 1)]

  return (
    <div>
      <p className="note">
        Evaluations are performed on anonymous labels (Response A/B/C). Model names are shown for readability.
      </p>
      <div className="tabs">
        {safeRankings.map((item, index) => (
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
        <ReactMarkdown>{current.raw_evaluation || ''}</ReactMarkdown>
      </div>

      <div className="panel ranking-box">
        <h4>Extracted Ranking</h4>
        {current.parsed_ranking?.length ? (
          <ol>
            {current.parsed_ranking.map((label) => (
              <li key={label}>
                <strong>{label}</strong>
                {metadata?.label_to_model?.[label] ? ` → ${metadata.label_to_model[label]}` : ''}
              </li>
            ))}
          </ol>
        ) : (
          <p>Could not parse ranking.</p>
        )}
      </div>

      {metadata?.aggregate_rankings?.length ? (
        <div className="panel ranking-box">
          <h4>Aggregate Rankings</h4>
          <ol>
            {metadata.aggregate_rankings.map((item) => (
              <li key={item.label}>
                <strong>{item.model}</strong> — avg position {item.average_position} ({item.vote_count} votes)
              </li>
            ))}
          </ol>
        </div>
      ) : null}
    </div>
  )
}
