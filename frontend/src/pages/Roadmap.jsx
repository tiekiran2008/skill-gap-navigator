import { useState, useEffect } from 'react'
import { useApp } from '../context/AppContext'

const STATUS_KEY = 'skill_roadmap_status'

function loadStatus() {
  try {
    return JSON.parse(localStorage.getItem(STATUS_KEY) || '{}')
  } catch {
    return {}
  }
}

function saveStatus(status) {
  localStorage.setItem(STATUS_KEY, JSON.stringify(status))
}

const getImportanceColor = (imp) => ({
  critical: 'bg-red-500/20 text-red-300 border-red-500/30',
  high: 'bg-orange-500/20 text-orange-300 border-orange-500/30',
  medium: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
  low: 'bg-sky-500/20 text-sky-300 border-sky-500/30',
}[imp] || 'bg-amber-500/20 text-amber-300 border-amber-500/30')

const getImportanceDot = (imp) => ({
  critical: 'border-red-500',
  high: 'border-orange-500',
  medium: 'border-amber-500',
  low: 'border-sky-500',
}[imp] || 'border-amber-500')

const STATUS_STYLES = {
  'Not Started': { bg: 'bg-gray-700', text: 'text-gray-300', border: 'border-gray-600', icon: '○' },
  'Learning': { bg: 'bg-blue-600/20', text: 'text-blue-300', border: 'border-blue-500/40', icon: '◑' },
  'Completed': { bg: 'bg-emerald-600/20', text: 'text-emerald-300', border: 'border-emerald-500/40', icon: '●' },
}

const DIFFICULTY_COLORS = {
  Beginner: 'bg-emerald-500/15 text-emerald-300',
  Intermediate: 'bg-blue-500/15 text-blue-300',
  Advanced: 'bg-purple-500/15 text-purple-300',
}

export default function Roadmap({ onNavigate }) {
  const { careerResult, companyAnalysis, skills } = useApp()
  const [roadmap, setRoadmap] = useState(null)
  const [status, setStatus] = useState({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [expandedSkill, setExpandedSkill] = useState(null)
  const [activePhase, setActivePhase] = useState(null)

  useEffect(() => {
    setStatus(loadStatus())
  }, [])

  useEffect(() => {
    const missingSkills = companyAnalysis?.missing_skills || careerResult?.missing_skills
    if (missingSkills && missingSkills.length > 0) {
      generateRoadmap(missingSkills)
    }
  }, [companyAnalysis, careerResult])

  async function generateRoadmap(missingSkills) {
    setLoading(true)
    setError(null)
    try {
      const userSkills = skills.map(s => s.name || s)
      const res = await fetch('/api/v1/roadmap/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          missing_skills: missingSkills,
          user_skills: userSkills,
          target_role: companyAnalysis?.role || careerResult?.target_role,
        }),
      })
      if (!res.ok) throw new Error('Failed to generate roadmap')
      const data = await res.json()
      setRoadmap(data)
      if (data.phases?.length > 0) {
        setActivePhase(data.phases[0].phase)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  function toggleStatus(skillId) {
    setStatus(prev => {
      const current = prev[skillId] || 'Not Started'
      const next = current === 'Not Started' ? 'Learning' : current === 'Learning' ? 'Completed' : 'Not Started'
      const updated = { ...prev, [skillId]: next }
      saveStatus(updated)
      return updated
    })
  }

  function getStatus(skillId) {
    return status[skillId] || 'Not Started'
  }

  function getCompletedCount() {
    if (!roadmap) return 0
    return roadmap.skills.filter(s => getStatus(s.id) === 'Completed').length
  }

  function getProgress() {
    if (!roadmap || roadmap.skills.length === 0) return 0
    return Math.round((getCompletedCount() / roadmap.skills.length) * 100)
  }

  const source = companyAnalysis
    ? `${companyAnalysis.company} — ${companyAnalysis.role}`
    : careerResult
    ? careerResult.target_role
    : null

  const missingSkills = companyAnalysis?.missing_skills || careerResult?.missing_skills

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold mb-1">Learning Roadmap</h1>
          <p className="text-sm text-gray-500">
            {source ? `Personalized roadmap for ${source}` : 'Complete an analysis to generate your roadmap'}
          </p>
        </div>
        {roadmap && (
          <div className="text-right">
            <div className="text-2xl font-bold text-violet-400">{getProgress()}%</div>
            <div className="text-xs text-gray-500">{getCompletedCount()}/{roadmap.skills.length} completed</div>
          </div>
        )}
      </div>

      {roadmap && (
        <div className="w-full bg-gray-800 rounded-full h-2">
          <div
            className="bg-gradient-to-r from-violet-500 to-emerald-500 h-2 rounded-full transition-all duration-500"
            style={{ width: `${getProgress()}%` }}
          />
        </div>
      )}

      {loading && (
        <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-12 text-center">
          <div className="inline-block w-8 h-8 border-2 border-violet-400 border-t-transparent rounded-full animate-spin mb-4" />
          <p className="text-sm text-gray-400">Generating your personalized roadmap...</p>
        </div>
      )}

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-6 text-center">
          <p className="text-red-300">{error}</p>
        </div>
      )}

      {!loading && !error && !roadmap && (
        <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-12 text-center">
          <div className="text-5xl mb-4">🗺️</div>
          <h3 className="text-lg font-semibold mb-2">No Roadmap Yet</h3>
          <p className="text-sm text-gray-500 mb-6">Upload your resume and run an analysis to generate your learning roadmap.</p>
          <button onClick={() => onNavigate('resume')} className="px-6 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-sm font-medium transition-colors">
            Get Started
          </button>
        </div>
      )}

      {!loading && roadmap && roadmap.skills.length === 0 && (
        <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-12 text-center">
          <div className="text-5xl mb-4">✅</div>
          <h3 className="text-lg font-semibold mb-2">Great Job!</h3>
          <p className="text-sm text-gray-500 max-w-md mx-auto">
            You already have all the required skills. Try analyzing a different career or company.
          </p>
          <div className="flex gap-3 justify-center mt-6">
            <button onClick={() => onNavigate('careers')} className="px-5 py-2 rounded-xl bg-violet-600 hover:bg-violet-500 text-sm font-medium transition-colors">
              Career Matches
            </button>
            <button onClick={() => onNavigate('companies')} className="px-5 py-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-sm font-medium transition-colors">
              Companies
            </button>
          </div>
        </div>
      )}

      {!loading && roadmap && roadmap.skills.length > 0 && (
        <div className="space-y-6">
          {roadmap.summary && (
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {[
                { label: 'Total', value: roadmap.summary.total_skills, color: 'text-white' },
                { label: 'Critical', value: roadmap.summary.critical, color: 'text-red-400' },
                { label: 'High', value: roadmap.summary.high, color: 'text-orange-400' },
                { label: 'Medium', value: roadmap.summary.medium, color: 'text-amber-400' },
                { label: 'Est. Weeks', value: `~${roadmap.summary.estimated_weeks}`, color: 'text-violet-400' },
              ].map((s, i) => (
                <div key={i} className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-xl p-3 text-center">
                  <p className={`text-xl font-bold ${s.color}`}>{s.value}</p>
                  <p className="text-[10px] text-gray-500">{s.label}</p>
                </div>
              ))}
            </div>
          )}

          {roadmap.phases.length > 0 && (
            <div className="flex gap-2 overflow-x-auto pb-2">
              {roadmap.phases.map(phase => (
                <button
                  key={phase.phase}
                  onClick={() => setActivePhase(activePhase === phase.phase ? null : phase.phase)}
                  className={`px-4 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition-colors ${
                    activePhase === phase.phase
                      ? 'bg-violet-600 text-white'
                      : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                  }`}
                >
                  {phase.name}
                  <span className="ml-2 text-xs opacity-60">({phase.skills.length})</span>
                </button>
              ))}
              <button
                onClick={() => setActivePhase(null)}
                className={`px-4 py-2 rounded-xl text-sm font-medium whitespace-nowrap transition-colors ${
                  activePhase === null
                    ? 'bg-violet-600 text-white'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
              >
                All ({roadmap.skills.length})
              </button>
            </div>
          )}

          <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-6">
            <div className="relative">
              <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-800" />

              <div className="space-y-4">
                {(activePhase !== null
                  ? roadmap.phases.filter(p => p.phase === activePhase).flatMap(p => p.skills)
                  : roadmap.skills
                ).map((item) => {
                  const st = getStatus(item.id)
                  const stStyle = STATUS_STYLES[st]
                  const isExpanded = expandedSkill === item.id

                  return (
                    <div key={item.id} className="relative flex gap-4">
                      <div className="relative z-10 mt-1 flex-shrink-0">
                        <button
                          onClick={() => toggleStatus(item.id)}
                          className={`w-8 h-8 rounded-full border-2 ${getImportanceDot(item.importance)} ${stStyle.bg} flex items-center justify-center transition-colors hover:scale-110`}
                          title={`Click to change status (current: ${st})`}
                        >
                          <span className={`text-xs ${stStyle.text}`}>{stStyle.icon}</span>
                        </button>
                      </div>

                      <div className="flex-1 pb-2">
                        <div
                          className={`rounded-xl border transition-colors cursor-pointer ${
                            st === 'Completed'
                              ? 'bg-emerald-500/5 border-emerald-500/20'
                              : 'bg-gray-800/50 border-gray-700/50 hover:border-gray-600'
                          }`}
                        >
                          <div className="p-4" onClick={() => setExpandedSkill(isExpanded ? null : item.id)}>
                            <div className="flex items-center justify-between mb-1">
                              <div className="flex items-center gap-2">
                                <span className={`font-semibold ${st === 'Completed' ? 'text-emerald-300 line-through opacity-70' : 'text-gray-200'}`}>
                                  {item.skill}
                                </span>
                                <span className={`px-1.5 py-0.5 rounded text-[9px] font-medium ${DIFFICULTY_COLORS[item.difficulty] || ''}`}>
                                  {item.difficulty}
                                </span>
                              </div>
                              <div className="flex items-center gap-2">
                                <span className={`px-2 py-0.5 rounded text-[10px] font-medium border ${getImportanceColor(item.importance)}`}>
                                  {item.importance}
                                </span>
                                <svg className={`w-4 h-4 text-gray-500 transition-transform ${isExpanded ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                                  <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
                                </svg>
                              </div>
                            </div>

                            <div className="flex items-center gap-3 text-xs text-gray-500">
                              <span className="flex items-center gap-1">
                                <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                {item.estimated_time}
                              </span>
                              <span className="text-gray-700">•</span>
                              <span>{item.category}</span>
                            </div>
                          </div>

                          {isExpanded && (
                            <div className="px-4 pb-4 border-t border-gray-700/30 pt-3 space-y-3">
                              {item.prerequisites.length > 0 && (
                                <div>
                                  <p className="text-[10px] text-gray-500 uppercase tracking-wide mb-1">Prerequisites</p>
                                  <div className="flex flex-wrap gap-1">
                                    {item.prerequisites.map((p, i) => (
                                      <span key={i} className="px-2 py-0.5 rounded bg-gray-700/50 text-gray-400 text-xs">
                                        {p}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                              )}

                              {item.topics.length > 0 && (
                                <div>
                                  <p className="text-[10px] text-gray-500 uppercase tracking-wide mb-1">Topics to Cover</p>
                                  <div className="flex flex-wrap gap-1">
                                    {item.topics.map((t, i) => (
                                      <span key={i} className="px-2 py-0.5 rounded bg-violet-500/10 text-violet-300 text-xs">
                                        {t}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                              )}

                              {item.project && (
                                <div>
                                  <p className="text-[10px] text-gray-500 uppercase tracking-wide mb-1">Hands-on Project</p>
                                  <p className="text-sm text-gray-300">{item.project}</p>
                                </div>
                              )}

                              <button
                                onClick={(e) => { e.stopPropagation(); toggleStatus(item.id) }}
                                className={`w-full py-2 rounded-lg text-xs font-medium transition-colors ${
                                  st === 'Completed'
                                    ? 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                                    : st === 'Learning'
                                    ? 'bg-emerald-600 hover:bg-emerald-500 text-white'
                                    : 'bg-blue-600 hover:bg-blue-500 text-white'
                                }`}
                              >
                                {st === 'Completed' ? 'Mark as Not Started' : st === 'Learning' ? 'Mark as Completed' : 'Start Learning'}
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
