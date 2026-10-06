import { useState, useEffect } from 'react'
import { useApp } from '../context/AppContext'

const API = '/api'

export default function JobMarket() {
  const { skills } = useApp()
  const [overview, setOverview] = useState(null)
  const [selectedRole, setSelectedRole] = useState('')
  const [roleData, setRoleData] = useState(null)
  const [userAnalysis, setUserAnalysis] = useState(null)
  const [selectedCompany, setSelectedCompany] = useState('')
  const [companyData, setCompanyData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadOverview()
  }, [])

  useEffect(() => {
    if (selectedRole) loadRoleData(selectedRole)
  }, [selectedRole])

  useEffect(() => {
    if (skills.length > 0) loadUserAnalysis()
  }, [skills, selectedRole])

  useEffect(() => {
    if (selectedCompany) loadCompanyData(selectedCompany)
  }, [selectedCompany])

  async function loadOverview() {
    setLoading(true)
    try {
      const res = await fetch(`${API}/v1/market/roles`)
      if (!res.ok) throw new Error('Failed to load market data')
      setOverview(await res.json())
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  async function loadRoleData(role) {
    try {
      const res = await fetch(`${API}/v1/market/skills?role=${encodeURIComponent(role)}`)
      if (res.ok) setRoleData(await res.json())
    } catch {}
  }

  async function loadUserAnalysis() {
    try {
      const res = await fetch(`${API}/v1/market/analyze-user`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ skills, target_role: selectedRole || undefined }),
      })
      if (res.ok) setUserAnalysis(await res.json())
    } catch {}
  }

  async function loadCompanyData(company) {
    try {
      const res = await fetch(`${API}/v1/market/company/${encodeURIComponent(company)}`)
      if (res.ok) setCompanyData(await res.json())
      else setCompanyData(null)
    } catch { setCompanyData(null) }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="inline-block w-8 h-8 border-2 border-violet-400 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (error) {
    return <div className="text-center py-20 text-red-400">{error}</div>
  }

  const roles = overview?.role_demand?.roles || []
  const topSkills = overview?.skill_demand?.top_skills || []
  const companies = overview?.companies || []
  const roleSkills = roleData?.top_skills || []

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold mb-1">Job Market Intelligence</h1>
        <p className="text-sm text-gray-500">Dataset-based analysis of skill and role demand across 8 companies</p>
      </div>

      {/* Top Roles */}
      <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-6">
        <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Top Roles by Demand</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {roles.slice(0, 8).map(r => (
            <button
              key={r.role}
              onClick={() => setSelectedRole(selectedRole === r.role ? '' : r.role)}
              className={`p-3 rounded-xl border text-left transition-all ${
                selectedRole === r.role
                  ? 'bg-violet-500/15 border-violet-500/30 text-violet-300'
                  : 'bg-gray-800/50 border-gray-700/50 hover:border-gray-600'
              }`}
            >
              <p className="text-sm font-medium truncate">{r.role}</p>
              <p className="text-xs text-gray-500 mt-1">{r.openings} openings</p>
              <div className="mt-2 h-1.5 bg-gray-700 rounded-full overflow-hidden">
                <div className="h-full bg-violet-500 rounded-full" style={{ width: `${r.demand_score}%` }} />
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Most In-Demand Skills */}
      <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-6">
        <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Most In-Demand Skills (All Roles)</h2>
        <div className="space-y-2.5">
          {topSkills.slice(0, 10).map((s, i) => (
            <div key={s.skill} className="flex items-center gap-3">
              <span className="text-xs text-gray-500 w-5 text-right">{i + 1}</span>
              <span className="text-sm w-40 truncate">{s.skill}</span>
              <div className="flex-1 h-2 bg-gray-800 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all"
                  style={{
                    width: `${s.demand_percentage}%`,
                    backgroundColor: s.demand_percentage >= 70 ? '#10b981' : s.demand_percentage >= 40 ? '#8b5cf6' : '#6b7280',
                  }}
                />
              </div>
              <span className="text-xs text-gray-400 w-10 text-right">{s.demand_percentage}%</span>
            </div>
          ))}
        </div>
      </div>

      {/* Role Detail + User Analysis */}
      {selectedRole && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Skill Demand for Role */}
          <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-6">
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-1">
              {selectedRole} — Top Demanded Skills
            </h2>
            <p className="text-xs text-gray-600 mb-4">{roleData?.total_jobs || 0} job postings in dataset</p>
            <div className="space-y-2.5">
              {roleSkills.slice(0, 10).map(s => (
                <div key={s.skill} className="flex items-center gap-3">
                  <span className="text-sm w-40 truncate">{s.skill}</span>
                  <div className="flex-1 h-2 bg-gray-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-emerald-500 rounded-full"
                      style={{ width: `${s.demand_percentage}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-400 w-10 text-right">{s.demand_percentage}%</span>
                </div>
              ))}
            </div>
          </div>

          {/* User Market Readiness */}
          <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-6">
            <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Your Market Readiness</h2>
            {userAnalysis ? (
              <div className="space-y-5">
                <div className="text-center">
                  <div className="inline-flex items-center justify-center w-20 h-20 rounded-full border-4 border-violet-500/30">
                    <span className="text-2xl font-bold text-violet-400">{userAnalysis.market_readiness}%</span>
                  </div>
                </div>

                <div>
                  <p className="text-[11px] text-gray-500 uppercase tracking-wider mb-2">Skills You Already Have</p>
                  <div className="flex flex-wrap gap-1.5">
                    {userAnalysis.high_demand_skills_user_has.length > 0
                      ? userAnalysis.high_demand_skills_user_has.map(s => (
                        <span key={s} className="px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 text-xs font-medium">{s}</span>
                      ))
                      : <span className="text-xs text-gray-600">None of the top skills yet</span>
                    }
                  </div>
                </div>

                <div>
                  <p className="text-[11px] text-gray-500 uppercase tracking-wider mb-2">High-Demand Missing Skills</p>
                  <div className="flex flex-wrap gap-1.5">
                    {userAnalysis.high_demand_skills_missing.map(s => (
                      <span key={s} className="px-2.5 py-1 rounded-lg bg-red-500/10 text-red-300 border border-red-500/20 text-xs font-medium">{s}</span>
                    ))}
                  </div>
                </div>

                {userAnalysis.recommended_next_skills.length > 0 && (
                  <div>
                    <p className="text-[11px] text-gray-500 uppercase tracking-wider mb-2">Recommended Next Skills</p>
                    <div className="space-y-1.5">
                      {userAnalysis.recommended_next_skills.slice(0, 5).map(s => (
                        <div key={s.skill} className="flex items-center justify-between bg-gray-800/50 rounded-lg px-3 py-2">
                          <span className="text-sm">{s.skill}</span>
                          <span className="text-xs text-violet-400">{s.demand_percentage}% demand</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-sm text-gray-500">Add skills in Resume Analyzer to see your market readiness.</p>
            )}
          </div>
        </div>
      )}

      {/* Companies in Dataset */}
      <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-6">
        <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Companies in Dataset</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
          {companies.map(c => (
            <button
              key={c}
              onClick={() => setSelectedCompany(selectedCompany === c ? '' : c)}
              className={`p-3 rounded-xl border text-left transition-all ${
                selectedCompany === c
                  ? 'bg-cyan-500/15 border-cyan-500/30 text-cyan-300'
                  : 'bg-gray-800/50 border-gray-700/50 hover:border-gray-600'
              }`}
            >
              <p className="text-sm font-medium">{c}</p>
            </button>
          ))}
        </div>

        {companyData && (
          <div className="border-t border-gray-800 pt-4 mt-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-sm font-semibold text-gray-300 mb-3">{companyData.company} — Roles</h3>
                <div className="space-y-2">
                  {companyData.roles.map(r => (
                    <div key={r.role} className="flex items-center justify-between bg-gray-800/50 rounded-lg px-3 py-2">
                      <span className="text-sm">{r.role}</span>
                      <span className="text-xs text-gray-500">{r.openings} openings</span>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-gray-300 mb-3">Required Skills</h3>
                <div className="space-y-2">
                  {companyData.required_skills.map(s => (
                    <div key={s.skill} className="flex items-center gap-3">
                      <span className="text-sm w-36 truncate">{s.skill}</span>
                      <div className="flex-1 h-1.5 bg-gray-800 rounded-full overflow-hidden">
                        <div className="h-full bg-cyan-500 rounded-full" style={{ width: `${(s.frequency / companyData.total_openings) * 100}%` }} />
                      </div>
                      <span className="text-xs text-gray-500 w-10 text-right">{s.frequency}×</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
