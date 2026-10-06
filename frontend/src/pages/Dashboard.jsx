import { useEffect, useState } from 'react'
import { useApp } from '../context/AppContext'

const ICON_COLORS = {
  'bg-emerald-500': 'bg-emerald-500/15 text-emerald-400',
  'bg-violet-500': 'bg-violet-500/15 text-violet-400',
  'bg-cyan-500': 'bg-cyan-500/15 text-cyan-400',
  'bg-amber-500': 'bg-amber-500/15 text-amber-400',
}

const GLOW_COLORS = {
  'bg-emerald-500': 'bg-emerald-500',
  'bg-violet-500': 'bg-violet-500',
  'bg-cyan-500': 'bg-cyan-500',
  'bg-amber-500': 'bg-amber-500',
}

const StatCard = ({ label, value, icon, color }) => (
  <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-5 relative overflow-hidden">
    <div className={`absolute top-0 right-0 w-20 h-20 rounded-bl-[3rem] ${GLOW_COLORS[color] || color} opacity-10`} />
    <div className="flex items-start justify-between">
      <div>
        <p className="text-[11px] text-gray-500 uppercase tracking-wider mb-1">{label}</p>
        <p className="text-2xl font-bold">{value}</p>
      </div>
      <div className={`w-10 h-10 rounded-xl ${ICON_COLORS[color] || 'bg-gray-500/15 text-gray-400'} flex items-center justify-center`}>
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d={icon} />
        </svg>
      </div>
    </div>
  </div>
)

export default function Dashboard({ onNavigate }) {
  const { skills, careerResult, companyRecommendations } = useApp()
  const [verification, setVerification] = useState(null)

  const bestMatch = companyRecommendations.length > 0 ? companyRecommendations[0] : null
  const missingCount = careerResult ? careerResult.missing_skills.length : 0

  useEffect(() => {
    fetch('/api/v1/skills/verification/summary')
      .then(res => res.json())
      .then(setVerification)
      .catch(() => setVerification(null))
  }, [])

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold mb-1">Dashboard</h1>
        <p className="text-sm text-gray-500">Your career intelligence overview</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Career Readiness"
          value={careerResult ? `${careerResult.match_percentage}%` : '--'}
          icon="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
          color="bg-emerald-500"
        />
        <StatCard
          label="Skills Found"
          value={skills.length || '--'}
          icon="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
          color="bg-violet-500"
        />
        <StatCard
          label="Best Company Match"
          value={bestMatch ? `${bestMatch.match_percentage}%` : '--'}
          icon="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
          color="bg-cyan-500"
        />
        <StatCard
          label="Missing Skills"
          value={missingCount || '--'}
          icon="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          color="bg-amber-500"
        />
      </div>

      {skills.length === 0 ? (
        <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-12 text-center">
          <div className="text-5xl mb-4">🎯</div>
          <h3 className="text-lg font-semibold mb-2">Get Started</h3>
          <p className="text-sm text-gray-500 max-w-md mx-auto mb-6">
            Upload your resume to extract skills, then explore career matches, company recommendations, and personalized learning roadmaps.
          </p>
          <button
            onClick={() => onNavigate('resume')}
            className="px-6 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-sm font-medium transition-colors"
          >
            Upload Resume
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {bestMatch && (
            <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-6">
              <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Top Company Match</h2>
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-500/20 to-cyan-500/20 border border-gray-700 flex items-center justify-center text-lg font-bold text-violet-300">
                  {bestMatch.company[0]}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold">{bestMatch.company}</span>
                    <span className="text-xs text-gray-500">{bestMatch.industry}</span>
                  </div>
                  <p className="text-sm text-gray-400">{bestMatch.role}</p>
                </div>
                <div className="text-right">
                  <p className={`text-2xl font-bold ${bestMatch.match_percentage >= 70 ? 'text-emerald-400' : bestMatch.match_percentage >= 50 ? 'text-amber-400' : 'text-red-400'}`}>
                    {bestMatch.match_percentage}%
                  </p>
                  <p className="text-[10px] text-gray-500">match</p>
                </div>
              </div>
              <div className="mt-4 h-2 bg-gray-800 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-700 ${bestMatch.match_percentage >= 70 ? 'bg-emerald-500' : bestMatch.match_percentage >= 50 ? 'bg-amber-500' : 'bg-red-500'}`}
                  style={{ width: `${bestMatch.match_percentage}%` }}
                />
              </div>
              <button
                onClick={() => onNavigate('companies')}
                className="mt-4 text-sm text-violet-400 hover:text-violet-300 transition-colors"
              >
                View all companies →
              </button>
            </div>
          )}

          {careerResult && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-5">
                <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Career Analysis</h3>
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-lg font-bold">{careerResult.target_role}</span>
                  <span className={`text-sm font-semibold ${careerResult.match_percentage >= 70 ? 'text-emerald-400' : careerResult.match_percentage >= 50 ? 'text-amber-400' : 'text-red-400'}`}>
                    {careerResult.match_percentage}%
                  </span>
                </div>
                <button
                  onClick={() => onNavigate('careers')}
                  className="text-sm text-violet-400 hover:text-violet-300 transition-colors"
                >
                  View details →
                </button>
              </div>
              <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-5">
                <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Skills Overview</h3>
                <div className="flex flex-wrap gap-1.5">
                  {skills.slice(0, 8).map((s, i) => (
                    <span key={i} className="px-2 py-0.5 rounded bg-violet-500/15 text-violet-300 text-[11px]">
                      {s}
                    </span>
                  ))}
                  {skills.length > 8 && (
                    <span className="px-2 py-0.5 rounded bg-gray-800 text-gray-400 text-[11px]">
                      +{skills.length - 8}
                    </span>
                  )}
                </div>
                <button
                  onClick={() => onNavigate('resume')}
                  className="mt-3 text-sm text-violet-400 hover:text-violet-300 transition-colors"
                >
                  Manage skills →
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {verification && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Skill Verification</h2>
            <button
              onClick={() => onNavigate('skill-assessment')}
              className="text-sm text-violet-400 hover:text-violet-300 transition-colors"
            >
              Take Assessment →
            </button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-5 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-20 h-20 rounded-bl-[3rem] bg-violet-500 opacity-10" />
              <p className="text-[11px] text-gray-500 uppercase tracking-wider mb-1">Skills Detected</p>
              <p className="text-2xl font-bold text-violet-400">{verification.total_detected ?? '--'}</p>
              <p className="text-[10px] text-gray-500 mt-1">from resume</p>
            </div>
            <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-5 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-20 h-20 rounded-bl-[3rem] bg-emerald-500 opacity-10" />
              <p className="text-[11px] text-gray-500 uppercase tracking-wider mb-1">Skills Verified</p>
              <p className="text-2xl font-bold text-emerald-400">{verification.total_verified ?? '--'}</p>
              <p className="text-[10px] text-gray-500 mt-1">score &ge; 70</p>
            </div>
            <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-5 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-20 h-20 rounded-bl-[3rem] bg-cyan-500 opacity-10" />
              <p className="text-[11px] text-gray-500 uppercase tracking-wider mb-1">Avg Assessment Score</p>
              <p className="text-2xl font-bold text-cyan-400">{verification.avg_score != null ? `${verification.avg_score}%` : '--'}</p>
            </div>
            <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-5 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-20 h-20 rounded-bl-[3rem] bg-amber-500 opacity-10" />
              <p className="text-[11px] text-gray-500 uppercase tracking-wider mb-1">Verification Rate</p>
              <p className="text-2xl font-bold text-amber-400">{verification.verification_rate != null ? `${verification.verification_rate}%` : '--'}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
