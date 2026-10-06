import { useState, useEffect } from 'react'
import { useApp } from '../context/AppContext'

const API = '/api'

function ScoreRing({ score }) {
  const color = score >= 70 ? '#10b981' : score >= 40 ? '#f59e0b' : '#ef4444'
  return (
    <div className="relative inline-flex items-center justify-center w-24 h-24">
      <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="42" fill="none" stroke="#1f2937" strokeWidth="8" />
        <circle cx="50" cy="50" r="42" fill="none" stroke={color} strokeWidth="8"
          strokeDasharray={`${score * 2.64} 264`} strokeLinecap="round" />
      </svg>
      <span className="absolute text-xl font-bold">{score}</span>
    </div>
  )
}

export default function ResumeInsights() {
  const { skills } = useApp()
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(false)
  const [resumeFile, setResumeFile] = useState(null)
  const [profile, setProfile] = useState(null)
  const [targetRole, setTargetRole] = useState('')
  const [roles] = useState([
    'AI/ML Engineer', 'Data Scientist', 'Data Analyst',
    'Backend Developer', 'Full Stack Developer', 'Computer Vision Engineer',
    'NLP Engineer', 'DevOps Engineer'
  ])

  const handleUpload = async () => {
    if (!resumeFile) return
    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('file', resumeFile)
      const res = await fetch(`${API}/v1/resume/analyze`, { method: 'POST', body: formData })
      if (res.ok) {
        const data = await res.json()
        setProfile(data)
        analyzeResume(data)
      }
    } catch {}
    finally { setLoading(false) }
  }

  const analyzeResume = async (prof) => {
    try {
      const res = await fetch(`${API}/v1/resume/improve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ profile: prof, target_role_skills: skills }),
      })
      if (res.ok) setAnalysis(await res.json())
    } catch {}
  }

  useEffect(() => {
    if (profile) analyzeResume(profile)
  }, [skills])

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold mb-1">Resume Insights</h1>
        <p className="text-sm text-gray-500">Upload your resume to get AI-powered improvement suggestions</p>
      </div>

      {/* Upload Section */}
      <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-6">
        <div className="flex items-center gap-4">
          <div className="flex-1">
            <input
              type="file"
              accept=".pdf"
              onChange={(e) => setResumeFile(e.target.files[0])}
              className="hidden"
              id="resume-upload"
            />
            <label htmlFor="resume-upload" className="cursor-pointer block w-full p-4 border-2 border-dashed border-gray-700 rounded-xl text-center hover:border-violet-500/40 transition-colors">
              <p className="text-sm text-gray-300">
                {resumeFile ? resumeFile.name : 'Click to select PDF resume'}
              </p>
            </label>
          </div>
          <button
            onClick={handleUpload}
            disabled={!resumeFile || loading}
            className="px-6 py-3 rounded-xl bg-violet-600 hover:bg-violet-500 disabled:bg-gray-700 disabled:text-gray-500 text-sm font-medium transition-colors"
          >
            {loading ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>
      </div>

      {/* Results */}
      {analysis && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Score Card */}
          <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-6 flex flex-col items-center justify-center">
            <p className="text-[11px] text-gray-500 uppercase tracking-wider mb-3">Resume Score</p>
            <ScoreRing score={analysis.resume_score} />
            <div className="mt-4 w-full space-y-1.5">
              {Object.entries(analysis.score_breakdown || {}).map(([key, val]) => (
                <div key={key} className="flex items-center justify-between text-xs">
                  <span className="text-gray-500 capitalize">{key.replace(/_/g, ' ')}</span>
                  <span className="text-gray-400">{val.score}/{val.max}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Strengths */}
          <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-6">
            <h3 className="text-sm font-semibold text-emerald-400 mb-3">Strengths</h3>
            {analysis.strengths.length > 0 ? (
              <ul className="space-y-2">
                {analysis.strengths.map((s, i) => (
                  <li key={i} className="flex items-start gap-2 text-xs text-gray-400">
                    <span className="text-emerald-400 mt-0.5">✓</span>
                    <span>{s}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-xs text-gray-600">No strengths detected yet.</p>
            )}

            <h3 className="text-sm font-semibold text-amber-400 mt-5 mb-3">Improvements</h3>
            {analysis.improvements.length > 0 ? (
              <ul className="space-y-2">
                {analysis.improvements.map((s, i) => (
                  <li key={i} className="flex items-start gap-2 text-xs text-gray-400">
                    <span className="text-amber-400 mt-0.5">!</span>
                    <span>{s}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-xs text-gray-600">No improvements needed.</p>
            )}
          </div>

          {/* Missing Sections & Keywords */}
          <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-6">
            <h3 className="text-sm font-semibold text-red-400 mb-3">Missing Sections</h3>
            {analysis.missing_sections.length > 0 ? (
              <div className="flex flex-wrap gap-1.5 mb-5">
                {analysis.missing_sections.map(s => (
                  <span key={s} className="px-2.5 py-1 rounded-lg bg-red-500/10 text-red-300 border border-red-500/20 text-xs capitalize">{s}</span>
                ))}
              </div>
            ) : (
              <p className="text-xs text-gray-600 mb-5">All key sections present.</p>
            )}

            <h3 className="text-sm font-semibold text-violet-400 mb-3">Target Role Keywords</h3>
            {analysis.target_role_keywords.length > 0 ? (
              <div className="flex flex-wrap gap-1.5 mb-5">
                {analysis.target_role_keywords.map(k => (
                  <span key={k} className="px-2.5 py-1 rounded-lg bg-violet-500/10 text-violet-300 border border-violet-500/20 text-xs">{k}</span>
                ))}
              </div>
            ) : (
              <p className="text-xs text-gray-600 mb-5">Select a target role to see keyword gaps.</p>
            )}

            <h3 className="text-sm font-semibold text-cyan-400 mb-3">Skill Suggestions</h3>
            {analysis.skill_improvements.length > 0 ? (
              <ul className="space-y-1.5">
                {analysis.skill_improvements.map((s, i) => (
                  <li key={i} className="text-xs text-gray-400">• {s}</li>
                ))}
              </ul>
            ) : (
              <p className="text-xs text-gray-600">No skill suggestions.</p>
            )}
          </div>
        </div>
      )}

      {/* Project Improvements */}
      {analysis?.project_improvements?.length > 0 && (
        <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-6">
          <h3 className="text-sm font-semibold text-amber-400 mb-3">Project Section Improvements</h3>
          <ul className="space-y-2">
            {analysis.project_improvements.map((s, i) => (
              <li key={i} className="flex items-start gap-2 text-xs text-gray-400">
                <span className="text-amber-400 mt-0.5">!</span>
                <span>{s}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {!analysis && !loading && (
        <div className="text-center py-12 text-gray-500 text-sm">
          Upload your resume to see improvement suggestions.
        </div>
      )}
    </div>
  )
}
