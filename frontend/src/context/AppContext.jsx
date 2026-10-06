import { createContext, useContext, useState, useEffect, useCallback } from 'react'

const AppContext = createContext()

const LS_KEY = 'sgn_state'

function loadLocal() {
  try {
    const raw = localStorage.getItem(LS_KEY)
    return raw ? JSON.parse(raw) : {}
  } catch { return {} }
}

function saveLocal(data) {
  try { localStorage.setItem(LS_KEY, JSON.stringify(data)) } catch {}
}

export function AppProvider({ children }) {
  const [skills, setSkillsState] = useState(() => loadLocal().skills || [])
  const [careers, setCareers] = useState([])
  const [careerResult, setCareerResult] = useState(null)
  const [companyRecommendations, setCompanyRecommendations] = useState([])
  const [companyAnalysis, setCompanyAnalysis] = useState(null)
  const [error, setError] = useState('')

  const setSkills = useCallback((val) => {
    setSkillsState(val)
    saveLocal({ ...loadLocal(), skills: val })
  }, [])

  useEffect(() => {
    const saved = loadLocal()
    if (saved.skills) setSkillsState(saved.skills)
  }, [])

  return (
    <AppContext.Provider value={{
      skills, setSkills,
      careers, setCareers,
      careerResult, setCareerResult,
      companyRecommendations, setCompanyRecommendations,
      companyAnalysis, setCompanyAnalysis,
      error, setError
    }}>
      {children}
    </AppContext.Provider>
  )
}

export function useApp() {
  return useContext(AppContext)
}
