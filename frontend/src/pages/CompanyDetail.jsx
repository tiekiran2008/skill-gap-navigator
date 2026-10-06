import { useApp } from '../context/AppContext'

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

const getImportanceColor = (imp) => ({
  critical: 'bg-red-500/20 text-red-300 border-red-500/30',
  high: 'bg-orange-500/20 text-orange-300 border-orange-500/30',
  medium: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
  low: 'bg-sky-500/20 text-sky-300 border-sky-500/30',
}[imp] || 'bg-amber-500/20 text-amber-300 border-amber-500/30')

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

export default function CompanyDetail({ onNavigate }) {
  const { companyAnalysis } = useApp()

  if (!companyAnalysis) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-2xl font-bold mb-1">Company Analysis</h1>
          <p className="text-sm text-gray-500">No analysis selected</p>
        </div>
        <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-12 text-center">
          <div className="text-5xl mb-4">📊</div>
          <h3 className="text-lg font-semibold mb-2">No Company Selected</h3>
          <p className="text-sm text-gray-500 mb-6">Go to Companies and select one to view its detailed analysis.</p>
          <button onClick={() => onNavigate('companies')} className="px-6 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-sm font-medium transition-colors">
            Browse Companies
          </button>
        </div>
      </div>
    )
  }

  const a = companyAnalysis

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${COMPANY_COLORS[a.company] || 'from-gray-500/20 to-gray-600/5'} border border-gray-700 flex items-center justify-center text-xl font-bold text-gray-300`}>
              {a.company[0]}
            </div>
            <div>
              <h1 className="text-2xl font-bold">{a.company}</h1>
              <p className="text-sm text-gray-400">{a.role}</p>
              {a.experience_level && (
                <p className="text-xs text-gray-600 mt-0.5">{a.experience_level}</p>
              )}
            </div>
          </div>
          <div className="text-right">
            <p className={`text-4xl font-bold ${getScoreColor(a.match_percentage)}`}>
              {a.match_percentage}%
            </p>
            <p className="text-xs text-gray-500">Overall Match</p>
          </div>
        </div>
        <div className="mt-4 h-3 bg-gray-800 rounded-full overflow-hidden">
          <div className={`h-full rounded-full transition-all duration-700 ${getBarColor(a.match_percentage)}`} style={{ width: `${a.match_percentage}%` }} />
        </div>
        {a.description && (
          <p className="mt-3 text-sm text-gray-500">{a.description}</p>
        )}
      </div>

      {/* Category Scores */}
      {a.category_scores && Object.keys(a.category_scores).length > 0 && (
        <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-6">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Readiness by Category</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {Object.entries(a.category_scores)
              .filter(([_, score]) => score > 0)
              .sort(([_, a], [__2, b]) => b - a)
              .map(([cat, score]) => (
                <div key={cat} className="p-3 rounded-xl bg-gray-800/50 border border-gray-700/50">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs text-gray-400">{cat}</span>
                    <span className={`text-sm font-bold ${getScoreColor(score)}`}>{score}%</span>
                  </div>
                  <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
                    <div className={`h-full rounded-full ${getBarColor(score)}`} style={{ width: `${score}%` }} />
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Required Skills */}
      <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-6">
        <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
          Required Skills <span className="text-gray-500">({a.required_skills.length})</span>
        </h2>
        <div className="flex flex-wrap gap-2">
          {a.required_skills.map((s, i) => {
            const isMatched = a.matched_skills.some(m => m.skill === s)
            const isPartial = a.partial_matches && a.partial_matches.some(m => m.skill === s)
            return (
              <span key={i} className={`px-3 py-1.5 rounded-xl text-xs font-medium border ${
                isMatched
                  ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20'
                  : isPartial
                    ? 'bg-amber-500/10 text-amber-300 border-amber-500/20'
                    : 'bg-gray-800/50 text-gray-400 border-gray-700'
              }`}>
                {isMatched && '✓ '}{isPartial && '~ '}{s}
              </span>
            )
          })}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Matched Skills */}
        <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-5">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
            Skills You Have <span className="text-emerald-400">({a.matched_skills.length})</span>
          </h2>
          <div className="space-y-2 max-h-72 overflow-y-auto">
            {a.matched_skills.map((s, i) => (
              <div key={i} className="flex items-center justify-between py-2 px-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
                <div>
                  <span className="text-sm text-emerald-300">{s.skill}</span>
                  <span className="text-[10px] text-emerald-400/50 ml-2">via {s.user_skill}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-1.5 py-0.5 rounded text-[9px] font-medium border ${getImportanceColor(s.importance)}`}>
                    {s.importance}
                  </span>
                  <span className="text-xs text-emerald-400/70">{Math.round(s.score * 100)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Missing Skills */}
        <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-5">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
            Missing Skills <span className="text-red-400">({a.missing_skills.length})</span>
          </h2>
          <div className="flex flex-wrap gap-2 max-h-72 overflow-y-auto">
            {a.missing_skills.map((s, i) => (
              <span key={i} className="px-3 py-1.5 rounded-xl bg-red-500/10 text-red-300 border border-red-500/20 text-xs">
                {s}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Partial Matches */}
      {a.partial_matches && a.partial_matches.length > 0 && (
        <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-5">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
            Partial Matches <span className="text-amber-400">({a.partial_matches.length})</span>
          </h2>
          <div className="flex flex-wrap gap-2">
            {a.partial_matches.map((s, i) => (
              <span key={i} className="px-3 py-1.5 rounded-xl bg-amber-500/10 text-amber-300 border border-amber-500/20 text-xs">
                {s.skill} <span className="text-amber-400/50">({Math.round(s.score * 100)}%)</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Preferred Skills */}
      {a.preferred_skills && a.preferred_skills.length > 0 && (
        <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-5">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Preferred Skills</h2>
          <div className="flex flex-wrap gap-2">
            {a.preferred_skills.map((s, i) => {
              const isMatched = a.matched_skills.some(m => m.skill === s)
              return (
                <span key={i} className={`px-3 py-1.5 rounded-xl text-xs font-medium border ${
                  isMatched
                    ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/20'
                    : 'bg-violet-500/10 text-violet-300 border-violet-500/20'
                }`}>
                  {isMatched && '✓ '}{s}
                </span>
              )
            })}
          </div>
        </div>
      )}

      {/* Priority Gaps */}
      {a.priority_gaps && a.priority_gaps.length > 0 && (
        <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-5">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Priority Skills to Learn</h2>
          <div className="flex flex-wrap gap-2">
            {a.priority_gaps.map((g, i) => (
              <span key={i} className={`px-3 py-1.5 rounded-xl text-xs font-medium border ${getImportanceColor(g.importance)}`}>
                #{i + 1} {g.skill}
              </span>
            ))}
          </div>
        </div>
      )}

      <button
        onClick={() => onNavigate('companies')}
        className="text-sm text-violet-400 hover:text-violet-300 transition-colors"
      >
        ← Back to Companies
      </button>
    </div>
  )
}
