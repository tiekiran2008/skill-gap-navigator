import { useState, useEffect, useCallback } from 'react';

const TARGET_ROLES = [
  'AI/ML Engineer',
  'Data Scientist',
  'Data Analyst',
  'Backend Developer',
  'Full Stack Developer',
  'Computer Vision Engineer',
  'NLP Engineer',
  'DevOps Engineer',
  'AI Agent Engineer',
];

const INTERVIEW_MODES = [
  { id: 'quick', label: 'Quick Interview', questions: 5, icon: '⚡' },
  { id: 'technical', label: 'Technical Interview', questions: 10, icon: '💻' },
  { id: 'project', label: 'Project Interview', questions: 8, icon: '📁' },
  { id: 'behavioral', label: 'Behavioral Interview', questions: 10, icon: '🗣' },
  { id: 'full', label: 'Full Mock Interview', questions: '15-20', icon: '🎯' },
];

const STAR_STEPS = [
  { letter: 'S', label: 'Situation', desc: 'Set the context' },
  { letter: 'T', label: 'Task', desc: 'Describe your responsibility' },
  { letter: 'A', label: 'Action', desc: 'Explain what you did' },
  { letter: 'R', label: 'Result', desc: 'Share the outcome' },
];

function CircularProgress({ value, label, color = 'violet' }) {
  const radius = 54;
  const stroke = 8;
  const normalizedRadius = radius - stroke;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (value / 100) * circumference;

  const colorMap = {
    violet: { stroke: '#8b5cf6', text: 'text-violet-400' },
    cyan: { stroke: '#06b6d4', text: 'text-cyan-400' },
    emerald: { stroke: '#10b981', text: 'text-emerald-400' },
    amber: { stroke: '#f59e0b', text: 'text-amber-400' },
  };

  const colors = colorMap[color] || colorMap.violet;

  return (
    <div className="flex flex-col items-center gap-2">
      <svg height={radius * 2} width={radius * 2} className="transform -rotate-90">
        <circle
          stroke="currentColor"
          className="text-gray-800"
          fill="transparent"
          strokeWidth={stroke}
          r={normalizedRadius}
          cx={radius}
          cy={radius}
        />
        <circle
          stroke={colors.stroke}
          fill="transparent"
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circumference + ' ' + circumference}
          style={{ strokeDashoffset, transition: 'stroke-dashoffset 0.8s ease-in-out' }}
          r={normalizedRadius}
          cx={radius}
          cy={radius}
        />
      </svg>
      <div className="absolute flex flex-col items-center justify-center">
        <span className={`text-2xl font-bold ${colors.text}`}>{Math.round(value)}%</span>
      </div>
      <span className="text-sm text-gray-400 text-center mt-1">{label}</span>
    </div>
  );
}

export default function InterviewPrep({ onNavigate }) {
  const [plan, setPlan] = useState(null);
  const [history, setHistory] = useState([]);
  const [targetRole, setTargetRole] = useState('');
  const [company, setCompany] = useState('');
  const [skills, setSkills] = useState('');
  const [expandedTopics, setExpandedTopics] = useState({});
  const [loadingPlan, setLoadingPlan] = useState(false);
  const [loadingInterview, setLoadingInterview] = useState(false);
  const [error, setError] = useState('');

  const fetchHistory = useCallback(async () => {
    try {
      const res = await fetch('/api/v1/interview/history');
      if (res.ok) {
        const data = await res.json();
        setHistory(Array.isArray(data) ? data : data.interviews || []);
      }
    } catch (e) {
      console.error('Failed to load interview history', e);
    }
  }, []);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const generatePlan = async () => {
    if (!targetRole) {
      setError('Please select a target role');
      return;
    }
    setError('');
    setLoadingPlan(true);
    try {
      const res = await fetch('/api/v1/interview/plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target_role: targetRole,
          company: company || undefined,
          skills: skills
            .split(',')
            .map((s) => s.trim())
            .filter(Boolean),
        }),
      });
      if (!res.ok) throw new Error('Failed to generate plan');
      const data = await res.json();
      setPlan(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoadingPlan(false);
    }
  };

  const startInterview = async (mode) => {
    setLoadingInterview(true);
    try {
      const res = await fetch('/api/v1/interview/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mode,
          target_role: targetRole || undefined,
          company: company || undefined,
          skills: skills
            .split(',')
            .map((s) => s.trim())
            .filter(Boolean),
        }),
      });
      if (!res.ok) throw new Error('Failed to start interview');
      const data = await res.json();
      if (onNavigate) onNavigate('mock-interview', data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoadingInterview(false);
    }
  };

  const toggleTopic = (topic) => {
    setExpandedTopics((prev) => ({ ...prev, [topic]: !prev[topic] }));
  };

  const readiness = plan?.readiness || {
    technical: 0,
    skill_confidence: 0,
    project: 0,
    overall: 0,
  };

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-4 md:p-8 max-w-7xl mx-auto">
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-white">Interview Preparation</h1>
        <p className="text-gray-400 mt-1">
          Generate a personalized study plan and practice with mock interviews
        </p>
      </header>

      {error && (
        <div className="mb-6 p-4 bg-red-950/50 border border-red-800 rounded-lg text-red-300">
          {error}
        </div>
      )}

      {/* Interview Readiness Card */}
      <section className="bg-gray-900 border border-gray-800 rounded-xl p-6 mb-8">
        <h2 className="text-xl font-semibold mb-6">Interview Readiness</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="relative flex flex-col items-center">
            <CircularProgress value={readiness.technical} label="Technical Readiness" color="violet" />
          </div>
          <div className="relative flex flex-col items-center">
            <CircularProgress
              value={readiness.skill_confidence}
              label="Verified Skill Confidence"
              color="cyan"
            />
          </div>
          <div className="relative flex flex-col items-center">
            <CircularProgress value={readiness.project} label="Project Readiness" color="emerald" />
          </div>
          <div className="relative flex flex-col items-center">
            <CircularProgress value={readiness.overall} label="Overall Interview Readiness" color="amber" />
          </div>
        </div>
      </section>

      {/* Target Role & Company Selection */}
      <section className="bg-gray-900 border border-gray-800 rounded-xl p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Target Role & Company</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Target Role</label>
            <select
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-gray-100 focus:outline-none focus:ring-2 focus:ring-violet-500"
            >
              <option value="">Select a role...</option>
              {TARGET_ROLES.map((role) => (
                <option key={role} value={role}>
                  {role}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Company (optional)</label>
            <input
              type="text"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              placeholder="e.g. Google, Meta..."
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Skills (comma separated)</label>
            <input
              type="text"
              value={skills}
              onChange={(e) => setSkills(e.target.value)}
              placeholder="e.g. Python, TensorFlow, React..."
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2.5 text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500"
            />
          </div>
        </div>
        <button
          onClick={generatePlan}
          disabled={loadingPlan}
          className="mt-4 px-6 py-2.5 bg-violet-600 hover:bg-violet-700 disabled:bg-violet-800 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors"
        >
          {loadingPlan ? 'Generating Plan...' : 'Generate Interview Plan'}
        </button>
      </section>

      {plan && (
        <>
          {/* Priority Topics */}
          {plan.priority_topics?.length > 0 && (
            <section className="bg-gray-900 border border-gray-800 rounded-xl p-6 mb-8">
              <h2 className="text-xl font-semibold mb-4">Priority Topics</h2>
              <div className="space-y-3">
                {plan.priority_topics.map((topic, i) => (
                  <div
                    key={i}
                    className="flex items-start gap-4 p-4 bg-gray-800/50 rounded-lg border border-gray-700/50"
                  >
                    <span className="flex-shrink-0 w-8 h-8 rounded-full bg-violet-600 flex items-center justify-center text-sm font-bold">
                      {i + 1}
                    </span>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-white">{topic.skill || topic.name}</h3>
                      {topic.reason && (
                        <p className="text-sm text-gray-400 mt-1">{topic.reason}</p>
                      )}
                    </div>
                    {topic.priority_score != null && (
                      <span className="text-sm text-violet-400 font-medium whitespace-nowrap">
                        {topic.priority_score}%
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Technical Topics */}
          {plan.technical_topics && Object.keys(plan.technical_topics).length > 0 && (
            <section className="bg-gray-900 border border-gray-800 rounded-xl p-6 mb-8">
              <h2 className="text-xl font-semibold mb-4">Technical Topics</h2>
              <div className="space-y-3">
                {Object.entries(plan.technical_topics).map(([topic, questions]) => (
                  <div key={topic} className="border border-gray-700/50 rounded-lg overflow-hidden">
                    <button
                      onClick={() => toggleTopic(topic)}
                      className="w-full flex items-center justify-between p-4 bg-gray-800/50 hover:bg-gray-800 transition-colors text-left"
                    >
                      <span className="font-medium text-white">{topic}</span>
                      <div className="flex items-center gap-3">
                        <span className="text-sm text-gray-400">
                          {Array.isArray(questions) ? questions.length : 0} questions
                        </span>
                        <svg
                          className={`w-5 h-5 text-gray-400 transition-transform ${
                            expandedTopics[topic] ? 'rotate-180' : ''
                          }`}
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                        </svg>
                      </div>
                    </button>
                    {expandedTopics[topic] && (
                      <div className="p-4 space-y-2 bg-gray-900/50">
                        {(Array.isArray(questions) ? questions : []).map((q, qi) => (
                          <div key={qi} className="p-3 bg-gray-800/30 rounded border border-gray-700/30">
                            <p className="text-sm text-gray-200">
                              <span className="text-violet-400 font-medium mr-2">Q{qi + 1}</span>
                              {typeof q === 'string' ? q : q.question || q.text || JSON.stringify(q)}
                            </p>
                            {q.hint && (
                              <p className="text-xs text-gray-500 mt-1 ml-6">Hint: {q.hint}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Behavioral Questions */}
          {plan.behavioral_questions?.length > 0 && (
            <section className="bg-gray-900 border border-gray-800 rounded-xl p-6 mb-8">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold">Behavioral Questions</h2>
                <div className="flex gap-3">
                  {STAR_STEPS.map((step) => (
                    <div key={step.letter} className="flex items-center gap-1 text-xs text-gray-400">
                      <span className="w-5 h-5 rounded bg-cyan-600/20 text-cyan-400 flex items-center justify-center font-bold text-[10px]">
                        {step.letter}
                      </span>
                      <span className="hidden sm:inline">{step.label}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="space-y-3">
                {plan.behavioral_questions.map((q, i) => (
                  <div
                    key={i}
                    className="p-4 bg-gray-800/50 rounded-lg border border-gray-700/50"
                  >
                    <p className="text-gray-200">
                      <span className="text-cyan-400 font-medium mr-2">Q{i + 1}</span>
                      {typeof q === 'string' ? q : q.question || q.text || JSON.stringify(q)}
                    </p>
                    {(q.star_guide || q.guide) && (
                      <p className="text-xs text-gray-500 mt-2 ml-6">
                        STAR Guide: {q.star_guide || q.guide}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Project Questions */}
          {plan.project_questions?.length > 0 && (
            <section className="bg-gray-900 border border-gray-800 rounded-xl p-6 mb-8">
              <h2 className="text-xl font-semibold mb-4">Project Questions</h2>
              <div className="space-y-3">
                {plan.project_questions.map((q, i) => (
                  <div
                    key={i}
                    className="p-4 bg-gray-800/50 rounded-lg border border-gray-700/50"
                  >
                    <p className="text-gray-200">
                      <span className="text-emerald-400 font-medium mr-2">Q{i + 1}</span>
                      {typeof q === 'string' ? q : q.question || q.text || JSON.stringify(q)}
                    </p>
                    {q.technologies && (
                      <div className="flex flex-wrap gap-2 mt-2 ml-6">
                        {(Array.isArray(q.technologies) ? q.technologies : [q.technologies]).map(
                          (tech, ti) => (
                            <span
                              key={ti}
                              className="text-xs px-2 py-0.5 bg-emerald-900/30 text-emerald-400 border border-emerald-800/50 rounded"
                            >
                              {tech}
                            </span>
                          )
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Start Mock Interview */}
          <section className="bg-gray-900 border border-gray-800 rounded-xl p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">Start Mock Interview</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {INTERVIEW_MODES.map((mode) => (
                <button
                  key={mode.id}
                  onClick={() => startInterview(mode.id)}
                  disabled={loadingInterview}
                  className="group p-5 bg-gray-800/50 border border-gray-700/50 rounded-xl hover:border-violet-500/50 hover:bg-gray-800 transition-all text-left disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <div className="text-2xl mb-2">{mode.icon}</div>
                  <h3 className="font-medium text-white group-hover:text-violet-300 transition-colors">
                    {mode.label}
                  </h3>
                  <p className="text-sm text-gray-400 mt-1">
                    {typeof mode.questions === 'number'
                      ? `${mode.questions} questions`
                      : `${mode.questions} questions`}
                  </p>
                </button>
              ))}
            </div>
          </section>
        </>
      )}

      {/* Recent Results */}
      <section className="bg-gray-900 border border-gray-800 rounded-xl p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Recent Results</h2>
        {history.length === 0 ? (
          <p className="text-gray-500 text-sm">
            No interview history yet. Complete a mock interview to see your results here.
          </p>
        ) : (
          <div className="space-y-3">
            {history.map((result, i) => (
              <div
                key={result.id || i}
                className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg border border-gray-700/50"
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3">
                    <span
                      className={`inline-block w-2 h-2 rounded-full ${
                        (result.score || 0) >= 80
                          ? 'bg-emerald-400'
                          : (result.score || 0) >= 60
                          ? 'bg-amber-400'
                          : 'bg-red-400'
                      }`}
                    />
                    <h3 className="font-medium text-white truncate">
                      {result.mode || result.type || 'Interview'}
                      {result.target_role && (
                        <span className="text-gray-400 font-normal ml-2">
                          — {result.target_role}
                        </span>
                      )}
                    </h3>
                  </div>
                  <p className="text-sm text-gray-400 mt-1 ml-5">
                    {result.date || result.created_at
                      ? new Date(result.date || result.created_at).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                          year: 'numeric',
                        })
                      : 'No date'}
                    {result.company && ` • ${result.company}`}
                  </p>
                </div>
                <div className="flex items-center gap-3 ml-4">
                  <div className="text-right">
                    <span
                      className={`text-lg font-bold ${
                        (result.score || 0) >= 80
                          ? 'text-emerald-400'
                          : (result.score || 0) >= 60
                          ? 'text-amber-400'
                          : 'text-red-400'
                      }`}
                    >
                      {result.score || 0}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
