import { useState, useEffect } from 'react'
import { useApp } from '../context/AppContext'

const API = '/api'

const getScoreColor = (pct) => {
  if (pct >= 70) return 'text-emerald-400'
  if (pct >= 50) return 'text-amber-400'
  return 'text-red-400'
}

const getBarColor = (pct) => {
  if (pct >= 70) return 'bg-emerald-500'
  if (pct >= 50) return 'bg-amber-500'
  return 'bg-red-500'
}

const COMPANY_COLORS = {
  Zoho: 'from-red-500/20 to-red-600/5',
  TCS: 'from-blue-500/20 to-blue-600/5',
  Infosys: 'from-sky-500/20 to-sky-600/5',
  Freshworks: 'from-indigo-500/20 to-indigo-600/5',
  Cognizant: 'from-blue-600/20 to-blue-700/5',
  Accenture: 'from-purple-500/20 to-purple-600/5',
  Amazon: 'from-amber-500/20 to-amber-600/5',
  Microsoft: 'from-cyan-500/20 to-cyan-600/5',
}

export default function Companies({ onNavigate }) {
  const { skills, companyRecommendations, setCompanyRecommendations, setCompanyAnalysis, error, setError } = useApp()
  const [loading, setLoading] = useState(false)
  const [verificationMap, setVerificationMap] = useState({})

  useEffect(() => {
    const fetchVerification = async () => {
      try {
        const res = await fetch(`${API}/v1/skills/verification`)
        if (!res.ok) return
        const data = await res.json()
        const map = {}
        const skillsObj = data.skills || {}
        if (Array.isArray(skillsObj)) {
          for (const item of skillsObj) {
            const name = item.skill || item.name
            if (name) map[name.toLowerCase()] = item.status
          }
        } else if (typeof skillsObj === 'object') {
          for (const [name, item] of Object.entries(skillsObj)) {
            map[name.toLowerCase()] = item.status
          }
        }
        setVerificationMap(map)
      } catch { /* ignore */ }
    }
    fetchVerification()
  }, [])

  const getVerificationBadge = (skillName) => {
    const status = verificationMap[skillName?.toLowerCase()]
    if (status === 'verified') return <span className="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400 ml-1" title="Verified" />
    if (status === 'needs_review') return <span className="inline-block w-1.5 h-1.5 rounded-full bg-amber-400 ml-1" title="Needs Review" />
    if (status === 'detected') return <span className="inline-block w-1.5 h-1.5 rounded-full bg-gray-400 ml-1" title="Detected" />
    return null
  }

  const fetchRecommendations = async () => {
    if (!skills.length) return
    setLoading(true)
    setError('')
    try {
      const res = await fetch(`${API}/v1/companies/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ skills }),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Failed to get recommendations')
      }
      const data = await res.json()
      setCompanyRecommendations(data.companies)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const viewAnalysis = async (company, role) => {
    setLoading(true)
    setError('')
    try {
      const res = await fetch(`${API}/v1/companies/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ skills, company, role }),
      })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Failed to analyze')
      }
      const data = await res.json()
      setCompanyAnalysis(data)
      onNavigate('company-detail')
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold mb-1">Companies</h1>
          <p className="text-sm text-gray-500">Discover which companies match your skill set</p>
        </div>
        <button
          onClick={fetchRecommendations}
          disabled={!skills.length || loading}
          className="px-5 py-2.5 rounded-xl font-medium bg-violet-600 hover:bg-violet-500 disabled:bg-gray-700 disabled:text-gray-500 transition-colors text-sm"
        >
          {loading ? 'Analyzing...' : companyRecommendations.length ? 'Refresh' : 'Find Matches'}
        </button>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-300 text-sm">{error}</div>
      )}

      {skills.length === 0 ? (
        <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-12 text-center">
          <div className="text-5xl mb-4">🏢</div>
          <h3 className="text-lg font-semibold mb-2">No Skills Found</h3>
          <p className="text-sm text-gray-500 mb-6">Upload your resume first to get company recommendations.</p>
          <button onClick={() => onNavigate('resume')} className="px-6 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-sm font-medium transition-colors">
            Go to Resume Analyzer
          </button>
        </div>
      ) : companyRecommendations.length === 0 ? (
        <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-12 text-center">
          <div className="text-5xl mb-4">🔍</div>
          <h3 className="text-lg font-semibold mb-2">Ready to Explore</h3>
          <p className="text-sm text-gray-500 max-w-md mx-auto">
            Click "Find Matches" to see which companies and roles best fit your skills.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {companyRecommendations.map((c, i) => (
            <div key={i} className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-5 hover:border-gray-700 transition-colors">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={`w-11 h-11 rounded-xl bg-gradient-to-br ${COMPANY_COLORS[c.company] || 'from-gray-500/20 to-gray-600/5'} border border-gray-700 flex items-center justify-center text-sm font-bold text-gray-300`}>
                    {c.company[0]}
                  </div>
                  <div>
                    <h3 className="font-semibold">{c.company}</h3>
                    <p className="text-[11px] text-gray-500">{c.industry}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`text-xl font-bold ${getScoreColor(c.match_percentage)}`}>
                    {c.match_percentage}%
                  </p>
                  <p className="text-[10px] text-gray-500">match</p>
                </div>
              </div>

              <p className="text-sm text-gray-400 mb-1">{c.role}</p>
              {c.experience_level && (
                <p className="text-[11px] text-gray-600 mb-3">{c.experience_level}</p>
              )}

              <div className="h-2 bg-gray-800 rounded-full overflow-hidden mb-3">
                <div className={`h-full rounded-full transition-all duration-700 ${getBarColor(c.match_percentage)}`} style={{ width: `${c.match_percentage}%` }} />
              </div>

              <div className="flex items-center justify-between mb-4">
                <div className="flex gap-3">
                  <span className="text-[11px] text-emerald-400">
                    {c.matched_count} matched
                  </span>
                  <span className="text-[11px] text-red-400">
                    {c.missing_count} missing
                  </span>
                </div>
              </div>

              <div className="flex flex-wrap gap-1.5 mb-4">
                {c.matched_skills.slice(0, 4).map((s, j) => (
                  <span key={j} className="px-2 py-0.5 rounded-lg bg-emerald-500/10 text-emerald-300 text-[10px] inline-flex items-center">
                    {s.skill}{getVerificationBadge(s.skill)}
                  </span>
                ))}
                {c.matched_skills.length > 4 && (
                  <span className="px-2 py-0.5 rounded-lg bg-gray-800 text-gray-500 text-[10px]">
                    +{c.matched_skills.length - 4}
                  </span>
                )}
              </div>

              <button
                onClick={() => viewAnalysis(c.company, c.role)}
                disabled={loading}
                className="w-full py-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-sm font-medium text-gray-300 transition-colors"
              >
                View Analysis
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
