import { useState, useCallback } from 'react'
import { AppProvider, useApp } from './context/AppContext'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import ResumeAnalyzer from './pages/ResumeAnalyzer'
import CareerMatches from './pages/CareerMatches'
import Companies from './pages/Companies'
import CompanyDetail from './pages/CompanyDetail'
import Roadmap from './pages/Roadmap'
import CareerAssistant from './pages/CareerAssistant'
import JobMarket from './pages/JobMarket'
import Projects from './pages/Projects'
import ResumeInsights from './pages/ResumeInsights'
import SkillAssessment from './pages/SkillAssessment'
import InterviewPrep from './pages/InterviewPrep'
import MockInterview from './pages/MockInterview'

const PAGES = {
  dashboard: Dashboard,
  resume: ResumeAnalyzer,
  careers: CareerMatches,
  companies: Companies,
  'company-detail': CompanyDetail,
  roadmap: Roadmap,
  assistant: CareerAssistant,
  market: JobMarket,
  projects: Projects,
  'resume-insights': ResumeInsights,
  'skill-assessment': SkillAssessment,
  'interview-prep': InterviewPrep,
  'mock-interview': MockInterview,
}

function AppLayout() {
  const [page, setPage] = useState('dashboard')
  const [pageData, setPageData] = useState(null)
  const { setError } = useApp()

  const navigate = useCallback((p, data) => {
    setError('')
    setPage(p)
    setPageData(data || null)
  }, [setError])

  const PageComponent = PAGES[page] || Dashboard

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex">
      <Sidebar activePage={page} onNavigate={navigate} />
      <main className="flex-1 ml-64 min-h-screen overflow-y-auto">
        <div className="max-w-6xl mx-auto px-6 py-8">
          <PageComponent onNavigate={navigate} pageData={pageData} interviewData={pageData} />
        </div>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <AppProvider>
      <AppLayout />
    </AppProvider>
  )
}
