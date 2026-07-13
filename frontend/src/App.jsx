import { useEffect, useMemo, useState } from 'react'
import ChatInterface from './components/ChatInterface'
import Stage1 from './components/Stage1'
import Stage2 from './components/Stage2'
import Stage3 from './components/Stage3'
import { api } from './api'
import './App.css'

function latestAssistant(messages = []) {
  for (let i = messages.length - 1; i >= 0; i -= 1) {
    if (messages[i].role === 'assistant') return messages[i]
  }
  return null
}

export default function App() {
  const [conversations, setConversations] = useState([])
  const [activeConversationId, setActiveConversationId] = useState(null)
  const [conversation, setConversation] = useState(null)
  const [metadata, setMetadata] = useState(null)
  const [activeStage, setActiveStage] = useState('stage1')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const assistant = useMemo(() => latestAssistant(conversation?.messages), [conversation])

  const refreshConversations = async () => {
    const data = await api.listConversations()
    setConversations(data.conversations || [])
  }

  const loadConversation = async (id) => {
    const data = await api.getConversation(id)
    setConversation(data)
    setActiveConversationId(id)
    setMetadata(null)
  }

  const ensureConversation = async () => {
    if (activeConversationId) return activeConversationId
    const created = await api.createConversation()
    await refreshConversations()
    setActiveConversationId(created.id)
    setConversation(created)
    return created.id
  }

  const sendMessage = async (content) => {
    setError('')
    setLoading(true)
    try {
      const id = await ensureConversation()
      const result = await api.sendMessage(id, content)
      setConversation(result.conversation)
      setMetadata(result.metadata || null)
      await refreshConversations()
      setActiveStage('stage3')
    } catch (err) {
      setError(err.message || 'Request failed')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const init = async () => {
      try {
        await api.health()
        await refreshConversations()
      } catch (err) {
        setError('Backend is not reachable at http://localhost:8001')
      }
    }
    init()
  }, [])

  return (
    <div className="app-wrap">
      <aside className="sidebar">
        <h2>LLM Council</h2>
        <button
          type="button"
          onClick={async () => {
            setConversation(null)
            setMetadata(null)
            setActiveConversationId(null)
            await ensureConversation()
          }}
        >
          + New Chat
        </button>
        <div className="conversation-list">
          {conversations.map((item) => (
            <button
              key={item.id}
              type="button"
              className={item.id === activeConversationId ? 'active' : ''}
              onClick={() => loadConversation(item.id)}
            >
              {item.id.slice(0, 8)} · {item.message_count} msgs
            </button>
          ))}
        </div>
      </aside>

      <main className="main-pane">
        <header>
          <h1>LLM Council</h1>
          <p>Stage 1: first opinions · Stage 2: peer review · Stage 3: chairman synthesis</p>
        </header>

        <ChatInterface onSend={sendMessage} loading={loading} />
        {error ? <div className="error">{error}</div> : null}

        <div className="stage-tabs">
          <button type="button" className={activeStage === 'stage1' ? 'active' : ''} onClick={() => setActiveStage('stage1')}>Stage 1</button>
          <button type="button" className={activeStage === 'stage2' ? 'active' : ''} onClick={() => setActiveStage('stage2')}>Stage 2</button>
          <button type="button" className={activeStage === 'stage3' ? 'active' : ''} onClick={() => setActiveStage('stage3')}>Stage 3</button>
        </div>

        <section>
          {activeStage === 'stage1' ? <Stage1 responses={assistant?.stage1 || []} /> : null}
          {activeStage === 'stage2' ? <Stage2 rankings={assistant?.stage2 || []} metadata={metadata} /> : null}
          {activeStage === 'stage3' ? <Stage3 finalAnswer={assistant?.stage3 || ''} /> : null}
        </section>
      </main>
    </div>
  )
}
