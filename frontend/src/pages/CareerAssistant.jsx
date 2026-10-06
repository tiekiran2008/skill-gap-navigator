import { useState, useEffect, useRef } from 'react'

const QUICK_QUESTIONS = [
  "How ready am I for my target role?",
  "What should I learn next?",
  "Which skill gives me the biggest improvement?",
  "What projects should I build?",
  "Show my learning progress",
]

function renderMarkdown(text) {
  if (!text) return ''
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n- /g, '\n<li>')
    .replace(/\n(\d+)\. /g, '\n<li>')
    .split('\n')
    .map(line => {
      if (line.startsWith('<li>')) return `<ul><li>${line.slice(4)}</li></ul>`
      return line
    })
    .join('\n')
    .replace(/<\/ul>\n<ul>/g, '\n')
}

export default function CareerAssistant({ onNavigate }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [historyLoaded, setHistoryLoaded] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    loadHistory()
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function loadHistory() {
    try {
      const res = await fetch('/api/v1/assistant/history')
      if (res.ok) {
        const data = await res.json()
        if (data.history && data.history.length > 0) {
          setMessages(data.history.map(h => ({
            role: h.role,
            content: h.content,
            relevant_skills: h.relevant_skills || [],
            suggested_action: h.suggested_action || '',
            source: h.source || 'fallback',
          })))
        }
      }
    } catch (err) {
      console.error('Failed to load history:', err)
    } finally {
      setHistoryLoaded(true)
    }
  }

  async function sendMessage(text) {
    const msg = text || input.trim()
    if (!msg || loading) return

    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: msg }])
    setLoading(true)

    try {
      const res = await fetch('/api/v1/assistant/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg }),
      })

      if (!res.ok) throw new Error('Failed to get response')

      const data = await res.json()
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response,
        relevant_skills: data.relevant_skills || [],
        suggested_action: data.suggested_action || '',
        source: data.source || 'fallback',
      }])
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, something went wrong. Please try again.',
        relevant_skills: [],
        suggested_action: '',
        source: 'error',
      }])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  async function clearHistory() {
    try {
      await fetch('/api/v1/assistant/history', { method: 'DELETE' })
      setMessages([])
    } catch (err) {
      console.error('Failed to clear history:', err)
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-bold mb-1">Career Assistant</h1>
          <p className="text-sm text-gray-500">AI-powered guidance for your career development</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={clearHistory}
            className="px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-xs text-gray-400 transition-colors"
          >
            Clear Chat
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-4 mb-4 space-y-4">
        {!historyLoaded && (
          <div className="text-center py-8">
            <div className="inline-block w-6 h-6 border-2 border-violet-400 border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {historyLoaded && messages.length === 0 && (
          <div className="text-center py-12">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-500/20 to-cyan-500/20 border border-violet-500/20 flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 01.865-.501 48.172 48.172 0 003.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold mb-2">Ask Me Anything</h3>
            <p className="text-sm text-gray-500 max-w-md mx-auto mb-6">
              I can analyze your skills, explain career readiness, suggest learning paths, and help you improve your matches.
            </p>
            <div className="flex flex-wrap gap-2 justify-center max-w-lg mx-auto">
              {QUICK_QUESTIONS.map((q, i) => (
                <button
                  key={i}
                  onClick={() => sendMessage(q)}
                  className="px-3 py-1.5 rounded-lg bg-gray-800 border border-gray-700 text-xs text-gray-400 hover:border-violet-500/40 hover:text-violet-300 transition-all"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] ${msg.role === 'user' ? 'order-2' : ''}`}>
              <div className={`rounded-2xl px-4 py-3 text-sm ${
                msg.role === 'user'
                  ? 'bg-violet-600 text-white'
                  : 'bg-gray-800 border border-gray-700 text-gray-200'
              }`}>
                {msg.role === 'assistant' ? (
                  <div className="whitespace-pre-wrap" dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content) }} />
                ) : (
                  <p>{msg.content}</p>
                )}
              </div>

              {msg.role === 'assistant' && msg.relevant_skills && msg.relevant_skills.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {msg.relevant_skills.slice(0, 6).map((skill, j) => (
                    <span key={j} className="px-2 py-0.5 rounded bg-violet-500/10 text-violet-300 text-[10px]">
                      {skill}
                    </span>
                  ))}
                </div>
              )}

              {msg.role === 'assistant' && msg.suggested_action && (
                <div className="mt-2 flex items-center gap-2">
                  <span className="text-[10px] text-gray-500">Suggested:</span>
                  <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 text-[10px] font-medium">
                    {msg.suggested_action}
                  </span>
                </div>
              )}

              {msg.role === 'assistant' && msg.source && (
                <div className="mt-1 flex items-center gap-1">
                  <span className={`w-1.5 h-1.5 rounded-full ${msg.source === 'ai' ? 'bg-emerald-500' : 'bg-amber-500'}`} />
                  <span className="text-[9px] text-gray-600">
                    {msg.source === 'ai' ? 'AI' : 'Deterministic'}
                  </span>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-800 border border-gray-700 rounded-2xl px-4 py-3">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-violet-400 animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 rounded-full bg-violet-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 rounded-full bg-violet-400 animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="flex gap-2">
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about your career path, skill gaps, or learning progress..."
          disabled={loading}
          className="flex-1 bg-gray-900/80 backdrop-blur border border-gray-800 rounded-xl px-4 py-3 text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-violet-500 transition-colors disabled:opacity-50"
        />
        <button
          onClick={() => sendMessage()}
          disabled={!input.trim() || loading}
          className="px-5 py-3 rounded-xl bg-violet-600 hover:bg-violet-500 disabled:bg-gray-700 disabled:text-gray-500 text-sm font-medium transition-colors"
        >
          Send
        </button>
      </div>
    </div>
  )
}
