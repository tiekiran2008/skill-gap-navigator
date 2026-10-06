import { useState, useEffect } from 'react'
import { useApp } from '../context/AppContext'

const API = '/api'

const DIFF_COLORS = {
  Beginner: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/20',
  Intermediate: 'bg-amber-500/15 text-amber-300 border-amber-500/20',
  Advanced: 'bg-red-500/15 text-red-300 border-red-500/20',
}

export default function Projects({ onNavigate }) {
  const { skills, careerResult, companyAnalysis } = useApp()
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedProject, setSelectedProject] = useState(null)
  const [filterDifficulty, setFilterDifficulty] = useState('All')

  useEffect(() => { loadProjects() }, [])

  async function loadProjects() {
    setLoading(true)
    try {
      const missing = companyAnalysis?.missing_skills || careerResult?.missing_skills || []
      const targetRole = companyAnalysis?.role || careerResult?.target_role
      const res = await fetch(`${API}/v1/projects/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          skills,
          missing_skills: missing,
          target_role: targetRole,
        }),
      })
      if (res.ok) {
        const data = await res.json()
        setProjects(data.recommended_projects || [])
      }
    } catch {}
    finally { setLoading(false) }
  }

  const filtered = filterDifficulty === 'All'
    ? projects
    : projects.filter(p => p.difficulty === filterDifficulty)

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="inline-block w-8 h-8 border-2 border-violet-400 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold mb-1">Recommended Projects</h1>
        <p className="text-sm text-gray-500">Projects matched to your skill gaps and career goals</p>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-2">
        <span className="text-xs text-gray-500">Difficulty:</span>
        {['All', 'Beginner', 'Intermediate', 'Advanced'].map(d => (
          <button
            key={d}
            onClick={() => setFilterDifficulty(d)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              filterDifficulty === d
                ? 'bg-violet-500/15 text-violet-300 border border-violet-500/20'
                : 'bg-gray-800/50 text-gray-400 border border-transparent hover:border-gray-700'
            }`}
          >
            {d}
          </button>
        ))}
      </div>

      {/* Project Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.map(proj => (
          <div
            key={proj.id}
            className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-5 hover:border-gray-700 transition-all cursor-pointer"
            onClick={() => setSelectedProject(selectedProject?.id === proj.id ? null : proj)}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <h3 className="text-sm font-bold">{proj.title}</h3>
                <div className="flex items-center gap-2 mt-1.5">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-medium border ${DIFF_COLORS[proj.difficulty]}`}>
                    {proj.difficulty}
                  </span>
                  <span className="text-[11px] text-gray-500">{proj.estimated_duration}</span>
                </div>
              </div>
              <div className="text-right">
                <div className="text-lg font-bold text-violet-400">{proj.score}%</div>
                <div className="text-[10px] text-gray-500">match</div>
              </div>
            </div>

            {proj.missing_skills_covered.length > 0 && (
              <div className="mb-3">
                <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Covers your gaps</p>
                <div className="flex flex-wrap gap-1">
                  {proj.missing_skills_covered.map(s => (
                    <span key={s} className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 text-[11px]">{s}</span>
                  ))}
                </div>
              </div>
            )}

            <div className="mb-3">
              <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Tech Stack</p>
              <div className="flex flex-wrap gap-1">
                {proj.tech_stack.slice(0, 5).map(t => (
                  <span key={t} className="px-2 py-0.5 rounded bg-gray-800 text-gray-400 text-[11px]">{t}</span>
                ))}
              </div>
            </div>

            {selectedProject?.id === proj.id && (
              <div className="border-t border-gray-800 pt-3 mt-3 space-y-3">
                <p className="text-xs text-gray-400">{proj.description}</p>

                <div>
                  <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Features</p>
                  <ul className="text-xs text-gray-400 space-y-0.5">
                    {proj.features.map((f, i) => <li key={i}>• {f}</li>)}
                  </ul>
                </div>

                <div>
                  <p className="text-[10px] text-gray-500 uppercase tracking-wider mb-1">Why This Helps</p>
                  <ul className="text-xs text-gray-400 space-y-0.5">
                    {proj.why_recommended.map((w, i) => <li key={i}>• {w}</li>)}
                  </ul>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-[10px] text-gray-500">Resume value:</span>
                  <span className="text-[11px] text-cyan-400">{proj.resume_value}</span>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-[10px] text-gray-500">Skills gained:</span>
                  <div className="flex flex-wrap gap-1">
                    {proj.skills_you_will_gain.map(s => (
                      <span key={s} className="px-1.5 py-0.5 rounded bg-violet-500/10 text-violet-300 text-[10px]">{s}</span>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="text-center py-12 text-gray-500 text-sm">
          {projects.length === 0
            ? "Add skills in Resume Analyzer to get project recommendations."
            : "No projects match the selected filter."}
        </div>
      )}
    </div>
  )
}
