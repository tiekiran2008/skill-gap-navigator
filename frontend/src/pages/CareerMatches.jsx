import { useState, useEffect } from 'react'
import { useApp } from '../context/AppContext'

const API = '/api'

const getScoreColor = (pct) => {
  if (pct >= 75) return 'text-emerald-400'
  if (pct >= 50) return 'text-amber-400'
  return 'text-red-400'
}

const getBarColor = (pct) => {
  if (pct >= 75) return 'bg-emerald-500'
  if (pct >= 50) return 'bg-amber-500'
  return 'bg-red-500'
}

const getCategoryStyle = (cat) => ({
  'Best Fit': 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
  'Close Match': 'bg-amber-500/15 text-amber-300 border-amber-500/30',
  'Long-Term Goal': 'bg-sky-500/15 text-sky-300 border-sky-500/30',
}[cat] || 'bg-gray-500/15 text-gray-300 border-gray-500/30')

const getImportanceColor = (imp) => ({
  critical: 'bg-red-500/20 text-red-300 border-red-500/30',
  high: 'bg-orange-500/20 text-orange-300 border-orange-500/30',
  medium: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
  low: 'bg-sky-500/20 text-sky-300 border-sky-500/30',
}[imp] || 'bg-amber-500/20 text-amber-300 border-amber-500/30')

function ScoreBar({ label, value, color }) {
  return (
    <div className="flex items-center gap-3">
      <span className="text-[11px] text-gray-500 w-16 shrink-0">{label}</span>
      <div className="flex-1 h-1.5 bg-gray-800 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color || getBarColor(value)}`} style={{ width: `${value}%` }} />
      </div>
      <span className={`text-[11px] font-medium w-10 text-right ${getScoreColor(value)}`}>{value}%</span>
    </div>
  )
}

function RecommendationCard({ rec, onNavigate, onSelect, verificationMap }) {
  const [expanded, setExpanded] = useState(false)

  const getVerificationBadge = (skillName) => {
    const status = verificationMap[skillName.toLowerCase()]
    if (status === 'verified') {
      return <span title="Verified" className="inline-flex items-center justify-center w-3.5 h-3.5 rounded-full bg-emerald-500/20 text-emerald-400 text-[8px] leading-none">✓</span>
    }
    if (status === 'needs_review') {
      return <span title="Needs Review" className="inline-flex items-center justify-center w-3.5 h-3.5 rounded-full bg-orange-500/20 text-orange-400 text-[8px] leading-none">!</span>
    }
    return <span title="Detected from resume" className="inline-flex items-center justify-center w-3.5 h-3.5 rounded-full bg-gray-600/30 text-gray-500 text-[8px] leading-none">•</span>
  }

  return (
    <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-5 hover:border-gray-700 transition-colors">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-semibold text-gray-100">{rec.role}</h3>
            <span className={`px-2 py-0.5 rounded-lg text-[10px] font-medium border ${getCategoryStyle(rec.category)}`}>
              {rec.category}
            </span>
          </div>
          <p className="text-xs text-gray-500">
            {rec.total_matched}/{rec.total_required} skills matched
          </p>
        </div>
        <div className="text-right">
          <p className={`text-2xl font-bold ${getScoreColor(rec.score)}`}>{rec.score}</p>
          <p className="text-[10px] text-gray-500">score</p>
        </div>
      </div>

      <div className="h-2 bg-gray-800 rounded-full overflow-hidden mb-4">
        <div className={`h-full rounded-full transition-all duration-700 ${getBarColor(rec.score)}`} style={{ width: `${rec.score}%` }} />
      </div>

      <div className="space-y-1.5 mb-4">
        <ScoreBar label="Skills" value={rec.skill_match} />
        <ScoreBar label="Projects" value={rec.project_match} />
        <ScoreBar label="Experience" value={rec.experience_match} />
      </div>

      {rec.strongest_skills.length > 0 && (
        <div className="mb-3">
          <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1.5">Strongest Skills</p>
          <div className="flex flex-wrap gap-1.5">
            {rec.strongest_skills.map((s, i) => (
              <span key={i} className="px-2 py-0.5 rounded-lg bg-emerald-500/10 text-emerald-300 text-[10px] inline-flex items-center gap-1">
                {getVerificationBadge(s.skill)}
                {s.skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {rec.missing_skills.length > 0 && (
        <div className="mb-3">
          <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1.5">Missing Skills</p>
          <div className="flex flex-wrap gap-1.5">
            {rec.missing_skills.slice(0, 5).map((s, i) => (
              <span key={i} className="px-2 py-0.5 rounded-lg bg-red-500/10 text-red-300 text-[10px]">
                {s}
              </span>
            ))}
            {rec.missing_skills.length > 5 && (
              <span className="px-2 py-0.5 rounded-lg bg-gray-800 text-gray-500 text-[10px]">
                +{rec.missing_skills.length - 5}
              </span>
            )}
          </div>
        </div>
      )}

      {expanded && rec.reason.length > 0 && (
        <div className="mb-3 p-3 rounded-xl bg-gray-800/50 border border-gray-700/50">
          <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-2">Why This Role Matches</p>
          <ul className="space-y-1">
            {rec.reason.map((r, i) => (
              <li key={i} className="text-xs text-gray-400 flex items-start gap-2">
                <span className="text-violet-400 mt-0.5">•</span>
                {r}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="flex gap-2">
        <button
          onClick={() => setExpanded(!expanded)}
          className="flex-1 py-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-xs font-medium text-gray-300 transition-colors"
        >
          {expanded ? 'Less' : 'Why This Role?'}
        </button>
        <button
          onClick={() => {
            onSelect(rec)
            onNavigate('company-detail')
          }}
          className="flex-1 py-2 rounded-xl bg-violet-600/80 hover:bg-violet-500/80 text-xs font-medium text-violet-200 transition-colors"
        >
          View Roadmap
        </button>
      </div>
    </div>
  )
}

export default function CareerMatches({ onNavigate }) {
  const { skills, setCompanyAnalysis, error, setError } = useApp()
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(false)
  const [targetCareer, setTargetCareer] = useState('')
  const [verificationMap, setVerificationMap] = useState({})

  const fetchVerification = async () => {
    if (!skills.length) return
    try {
      const res = await fetch(`${API}/v1/skills/verification`)
      if (!res.ok) return
      const data = await res.json()
      const map = {}
      const skillsObj = data.skills || {}
      if (Array.isArray(skillsObj)) {
        for (const skill of skillsObj) {
          map[skill.skill?.toLowerCase() || skill.name?.toLowerCase()] = skill.status
        }
      } else if (typeof skillsObj === 'object') {
        for (const [name, item] of Object.entries(skillsObj)) {
          map[name.toLowerCase()] = item.status
        }
      }
      setVerificationMap(map)
    } catch {
    }
  }

  useEffect(() => {
    fetchVerification()
  }, [skills])

  const fetchRecommendations = async () => {
    if (!skills.length) return
    setLoading(true)
    setError('')
    try {
      const res = await fetch(`${API}/v1/careers/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ skills, target_career: targetCareer || undefined }),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Failed to get recommendations')
      }
      const data = await res.json()
      setRecommendations(data.recommendations)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const handleSelectRole = async (rec) => {
    setLoading(true)
    try {
      const res = await fetch(`${API}/v1/gap-analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ skills, target_role: rec.role }),
      })
      if (res.ok) {
        const data = await res.json()
        setCompanyAnalysis({
          company: rec.role,
          industry: 'Career Path',
          role: rec.role,
          match_percentage: data.overall_match || rec.score,
          required_skills: data.missing_skills || rec.missing_skills,
          preferred_skills: [],
          matched_skills: data.matched_skills || [],
          partial_matches: data.partial_matches || [],
          missing_skills: data.missing_skills || rec.missing_skills,
          priority_skills: data.priority_gaps?.map(g => g.skill) || [],
          roadmap: data.learning_path || data.roadmap || [],
        })
      }
    } catch {
    } finally {
      setLoading(false)
    }
  }

  const bestFit = recommendations.filter(r => r.category === 'Best Fit')
  const closeMatch = recommendations.filter(r => r.category === 'Close Match')
  const longTerm = recommendations.filter(r => r.category === 'Long-Term Goal')

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold mb-1">Career Matches</h1>
          <p className="text-sm text-gray-500">AI-powered career recommendations based on your profile</p>
        </div>
        <button
          onClick={fetchRecommendations}
          disabled={!skills.length || loading}
          className="px-5 py-2.5 rounded-xl font-medium bg-violet-600 hover:bg-violet-500 disabled:bg-gray-700 disabled:text-gray-500 transition-colors text-sm"
        >
          {loading ? 'Analyzing...' : recommendations.length ? 'Refresh' : 'Find Careers'}
        </button>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-300 text-sm">{error}</div>
      )}

      {skills.length === 0 ? (
        <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-12 text-center">
          <div className="text-5xl mb-4">📋</div>
          <h3 className="text-lg font-semibold mb-2">No Skills Found</h3>
          <p className="text-sm text-gray-500 mb-6">Upload your resume first to get career recommendations.</p>
          <button onClick={() => onNavigate('resume')} className="px-6 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-sm font-medium transition-colors">
            Go to Resume Analyzer
          </button>
        </div>
      ) : recommendations.length === 0 ? (
        <div className="space-y-6">
          <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-6">
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Target Career (Optional)</h2>
            <input
              type="text"
              value={targetCareer}
              onChange={(e) => setTargetCareer(e.target.value)}
              placeholder="e.g. AI/ML Engineer, Data Scientist..."
              className="w-full bg-gray-800 border border-gray-700 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-violet-500 transition-colors"
            />
          </div>
          <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-12 text-center">
            <div className="text-5xl mb-4">🎯</div>
            <h3 className="text-lg font-semibold mb-2">Ready to Discover</h3>
            <p className="text-sm text-gray-500 max-w-md mx-auto">
              Click "Find Careers" to see AI-powered career recommendations based on your skills, projects, and experience.
            </p>
          </div>
        </div>
      ) : (
        <div className="space-y-8">
          {bestFit.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-2 h-2 rounded-full bg-emerald-500" />
                <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Best Fit</h2>
                <span className="text-xs text-gray-600">({bestFit.length})</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {bestFit.map((rec, i) => (
                  <RecommendationCard key={i} rec={rec} onNavigate={onNavigate} onSelect={handleSelectRole} verificationMap={verificationMap} />
                ))}
              </div>
            </div>
          )}

          {closeMatch.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-2 h-2 rounded-full bg-amber-500" />
                <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Close Match</h2>
                <span className="text-xs text-gray-600">({closeMatch.length})</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {closeMatch.map((rec, i) => (
                  <RecommendationCard key={i} rec={rec} onNavigate={onNavigate} onSelect={handleSelectRole} verificationMap={verificationMap} />
                ))}
              </div>
            </div>
          )}

          {longTerm.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-2 h-2 rounded-full bg-sky-500" />
                <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Long-Term Goal</h2>
                <span className="text-xs text-gray-600">({longTerm.length})</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {longTerm.map((rec, i) => (
                  <RecommendationCard key={i} rec={rec} onNavigate={onNavigate} onSelect={handleSelectRole} verificationMap={verificationMap} />
                ))}
              </div>
            </div>
          )}

          <button
            onClick={() => onNavigate('companies')}
            className="w-full py-3 rounded-xl bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500 text-sm font-medium transition-all"
          >
            Explore Company Matches →
          </button>
        </div>
      )}
    </div>
  )
}
