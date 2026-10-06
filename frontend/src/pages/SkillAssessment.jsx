import { useState, useEffect, useCallback } from 'react';

export default function SkillAssessment({ onNavigate }) {
  const [skills, setSkills] = useState([]);
  const [selectedSkill, setSelectedSkill] = useState(null);
  const [difficulty, setDifficulty] = useState('BEGINNER');
  const [assessment, setAssessment] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [answers, setAnswers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [view, setView] = useState('select');
  const [history, setHistory] = useState([]);
  const [verification, setVerification] = useState([]);
  const [activeTab, setActiveTab] = useState('assess');
  const [results, setResults] = useState(null);

  useEffect(() => {
    fetchSkills();
    fetchHistory();
    fetchVerification();
  }, []);

  const fetchSkills = async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/v1/assessments/skills');
      if (!res.ok) throw new Error('Failed to fetch skills');
      const data = await res.json();
      setSkills(data.skills || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch('/api/v1/assessments/history');
      if (!res.ok) throw new Error('Failed to fetch history');
      const data = await res.json();
      setHistory(data.assessments || []);
    } catch (err) {
      console.error('Failed to fetch history:', err);
    }
  };

  const fetchVerification = async () => {
    try {
      const res = await fetch('/api/v1/skills/verification/summary');
      if (!res.ok) throw new Error('Failed to fetch verification');
      const data = await res.json();
      setVerification(data.skills ? Object.values(data.skills) : []);
    } catch (err) {
      console.error('Failed to fetch verification:', err);
    }
  };

  const startAssessment = useCallback(async () => {
    if (!selectedSkill) return;
    try {
      setLoading(true);
      setError(null);
      const res = await fetch('/api/v1/assessments/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ skill: selectedSkill.skill, difficulty }),
      });
      if (!res.ok) throw new Error('Failed to start assessment');
      const data = await res.json();
      setAssessment(data);
      setCurrentQuestionIndex(0);
      setSelectedAnswer(null);
      setAnswers([]);
      setView('assessment');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [selectedSkill, difficulty]);

  const submitAnswer = useCallback(async () => {
    if (!assessment || selectedAnswer === null) return;
    try {
      setLoading(true);
      setError(null);
      const question = assessment.questions[currentQuestionIndex];
      const res = await fetch(`/api/v1/assessments/${assessment.assessment_id}/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question_id: question.question_id, answer: selectedAnswer }),
      });
      if (!res.ok) throw new Error('Failed to submit answer');
      const data = await res.json();
      setAnswers((prev) => [...prev, data]);
      setSelectedAnswer(null);
      if (currentQuestionIndex + 1 < assessment.questions.length) {
        setCurrentQuestionIndex((prev) => prev + 1);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [assessment, currentQuestionIndex, selectedAnswer]);

  const completeAssessment = useCallback(async () => {
    if (!assessment) return;
    try {
      setLoading(true);
      setError(null);
      const res = await fetch(`/api/v1/assessments/${assessment.assessment_id}/complete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      if (!res.ok) throw new Error('Failed to complete assessment');
      const data = await res.json();
      setResults(data);
      setView('results');
      fetchHistory();
      fetchVerification();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [assessment]);

  const resetAssessment = () => {
    setAssessment(null);
    setResults(null);
    setSelectedAnswer(null);
    setAnswers([]);
    setCurrentQuestionIndex(0);
    setSelectedSkill(null);
    setView('select');
  };

  const difficultyColor = (d) => {
    switch (d) {
      case 'BEGINNER':
        return 'bg-green-100 text-green-800';
      case 'INTERMEDIATE':
        return 'bg-yellow-100 text-yellow-800';
      case 'ADVANCED':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const verificationStatus = (status) => {
    switch (status) {
      case 'VERIFIED':
        return { icon: '✓', color: 'text-green-400', bg: 'bg-green-400/10' };
      case 'DETECTED':
        return { icon: '○', color: 'text-gray-400', bg: 'bg-gray-400/10' };
      case 'NEEDS_REVIEW':
        return { icon: '!', color: 'text-orange-400', bg: 'bg-orange-400/10' };
      default:
        return { icon: '?', color: 'text-gray-500', bg: 'bg-gray-500/10' };
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  if (view === 'select') {
    return (
      <div className="min-h-screen bg-gray-900 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-100">Skill Assessment</h1>
              <p className="text-gray-400 mt-1">Test and verify your skills with AI-powered assessments</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setActiveTab('assess')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  activeTab === 'assess'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                }`}
              >
                Assessment
              </button>
              <button
                onClick={() => setActiveTab('history')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  activeTab === 'history'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                }`}
              >
                History
              </button>
              <button
                onClick={() => setActiveTab('verification')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  activeTab === 'verification'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                }`}
              >
                Verification
              </button>
            </div>
          </div>

          {error && (
            <div className="bg-red-900/30 border border-red-700 text-red-300 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          {activeTab === 'assess' && (
            <>
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-300 mb-2">Select Difficulty</label>
                <div className="flex gap-3">
                  {['BEGINNER', 'INTERMEDIATE', 'ADVANCED'].map((d) => (
                    <button
                      key={d}
                      onClick={() => setDifficulty(d)}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                        difficulty === d
                          ? 'ring-2 ring-blue-500 ' + difficultyColor(d)
                          : difficultyColor(d) + ' opacity-60 hover:opacity-100'
                      }`}
                    >
                      {d.charAt(0) + d.slice(1).toLowerCase()}
                    </button>
                  ))}
                </div>
              </div>

              <h2 className="text-xl font-semibold text-gray-100 mb-4">Choose a Skill</h2>
              {loading && skills.length === 0 ? (
                <div className="text-center py-12 text-gray-400">Loading skills...</div>
              ) : (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {skills.map((skill) => (
                    <button
                      key={skill.skill}
                      onClick={() => setSelectedSkill(skill)}
                      className={`p-4 rounded-xl border-2 text-left transition-all hover:scale-[1.02] ${
                        selectedSkill?.skill === skill.skill
                          ? 'border-blue-500 bg-blue-500/10'
                          : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                      }`}
                    >
                      <div className="text-gray-100 font-medium">{skill.skill}</div>
                      {skill.difficulties && skill.difficulties.length > 0 && (
                        <div className="text-gray-400 text-sm mt-1">{skill.difficulties.join(', ')}</div>
                      )}
                    </button>
                  ))}
                </div>
              )}

              {selectedSkill && (
                <div className="mt-8 flex justify-center">
                  <button
                    onClick={startAssessment}
                    disabled={loading}
                    className="px-8 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-semibold rounded-xl transition-colors text-lg"
                  >
                    {loading ? 'Starting...' : `Start Assessment: ${selectedSkill.skill}`}
                  </button>
                </div>
              )}
            </>
          )}

          {activeTab === 'history' && (
            <div className="space-y-3">
              {history.length === 0 ? (
                <div className="text-center py-12 text-gray-400">No assessment history yet.</div>
              ) : (
                history.map((item) => (
                  <div
                    key={item.id}
                    className="bg-gray-800 border border-gray-700 rounded-xl p-4 flex items-center justify-between"
                  >
                    <div>
                      <div className="text-gray-100 font-medium">{item.skill}</div>
                      <div className="text-gray-400 text-sm">
                        {new Date(item.completed_at || item.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className={`text-sm font-medium ${difficultyColor(item.difficulty)}`}>
                        {item.difficulty}
                      </span>
                      {item.score != null && (
                        <span className={`text-lg font-bold ${getScoreColor(item.score)}`}>
                          {item.score}%
                        </span>
                      )}
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium ${
                          item.status === 'completed'
                            ? 'bg-green-900/30 text-green-400'
                            : 'bg-yellow-900/30 text-yellow-400'
                        }`}
                      >
                        {item.status}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === 'verification' && (
            <div className="space-y-3">
              {verification.length === 0 ? (
                <div className="text-center py-12 text-gray-400">No verification data yet.</div>
              ) : (
                verification.map((item) => {
                  const vs = verificationStatus(item.status?.toUpperCase());
                  return (
                    <div
                      key={item.skillId || item.id || item.skill}
                      className="bg-gray-800 border border-gray-700 rounded-xl p-4 flex items-center justify-between"
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className={`w-10 h-10 rounded-full flex items-center justify-center text-lg font-bold ${vs.bg} ${vs.color}`}
                        >
                          {vs.icon}
                        </div>
                        <div>
                          <div className="text-gray-100 font-medium">{item.skillName || item.skill}</div>
                          <div className="text-gray-400 text-sm capitalize">
                            {item.status?.replace('_', ' ').toLowerCase()}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        {item.score != null && (
                          <div className={`text-sm font-medium ${getScoreColor(item.score)}`}>
                            Score: {item.score}%
                          </div>
                        )}
                        {item.attempts != null && (
                          <div className="text-gray-400 text-xs">
                            {item.attempts} attempt{item.attempts !== 1 ? 's' : ''}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          )}
        </div>
      </div>
    );
  }

  if (view === 'assessment') {
    const total = assessment?.questions?.length || 0;
    const answered = answers.length;
    const progress = total > 0 ? (answered / total) * 100 : 0;
    const question = assessment?.questions?.[currentQuestionIndex];

    return (
      <div className="min-h-screen bg-gray-900 p-6">
        <div className="max-w-3xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold text-gray-100">
              {assessment.skillName || 'Assessment'}
            </h1>
            <button
              onClick={resetAssessment}
              className="text-gray-400 hover:text-gray-200 transition-colors"
            >
              ✕ Exit
            </button>
          </div>

          <div className="mb-6">
            <div className="flex justify-between text-sm text-gray-400 mb-2">
              <span>Question {answered + (question && selectedAnswer === null ? 0 : 0)} of {total}</span>
              <span>{Math.round(progress)}% Complete</span>
            </div>
            <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-600 rounded-full transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>

          {error && (
            <div className="bg-red-900/30 border border-red-700 text-red-300 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          {question ? (
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
              <h2 className="text-lg text-gray-100 font-medium mb-6">{question.question}</h2>

              <div className="space-y-3">
                {question.options?.map((option, idx) => (
                  <button
                    key={idx}
                    onClick={() => setSelectedAnswer(idx)}
                    className={`w-full text-left px-4 py-3 rounded-lg border-2 transition-all ${
                      selectedAnswer === idx
                        ? 'border-blue-500 bg-blue-500/10 text-gray-100'
                        : 'border-gray-600 bg-gray-700/50 text-gray-300 hover:border-gray-500'
                    }`}
                  >
                    <span className="font-medium mr-3">{String.fromCharCode(65 + idx)}.</span>
                    {option}
                  </button>
                ))}
              </div>

              <div className="mt-8 flex justify-between">
                <div />
                {answered < total ? (
                  <button
                    onClick={submitAnswer}
                    disabled={selectedAnswer === null || loading}
                    className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white font-medium rounded-lg transition-colors"
                  >
                    {loading ? 'Submitting...' : 'Submit Answer'}
                  </button>
                ) : (
                  <button
                    onClick={completeAssessment}
                    disabled={loading}
                    className="px-6 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white font-medium rounded-lg transition-colors"
                  >
                    {loading ? 'Finishing...' : 'Complete Assessment'}
                  </button>
                )}
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-400">Loading question...</div>
          )}
        </div>
      </div>
    );
  }

  if (view === 'results') {
    const correct = results?.correctCount ?? answers.filter((a) => a.correct).length;
    const incorrect = results?.incorrectCount ?? answers.filter((a) => !a.correct).length;
    const total = results?.totalCount ?? answers.length;
    const score = results?.score ?? (total > 0 ? Math.round((correct / total) * 100) : 0);

    return (
      <div className="min-h-screen bg-gray-900 p-6">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-100 mb-2">Assessment Complete</h1>
            <p className="text-gray-400">{results?.skill || selectedSkill?.skill || 'Skill Assessment'}</p>
          </div>

          <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 mb-6">
            <div className="text-center mb-6">
              <div className={`text-6xl font-bold ${getScoreColor(score)}`}>{score}%</div>
              <div className="text-gray-400 mt-2">Overall Score</div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="bg-green-900/20 border border-green-700/30 rounded-lg p-4 text-center">
                <div className="text-3xl font-bold text-green-400">{correct}</div>
                <div className="text-green-300/70 text-sm">Correct</div>
              </div>
              <div className="bg-red-900/20 border border-red-700/30 rounded-lg p-4 text-center">
                <div className="text-3xl font-bold text-red-400">{incorrect}</div>
                <div className="text-red-300/70 text-sm">Incorrect</div>
              </div>
            </div>

            {results?.passed !== undefined && (
              <div className="mt-6 text-center">
                <span
                  className={`inline-block px-4 py-2 rounded-full text-sm font-semibold ${
                    results.passed
                      ? 'bg-green-900/30 text-green-400'
                      : 'bg-red-900/30 text-red-400'
                  }`}
                >
                  {results.passed ? 'PASSED' : 'FAILED'}
                </span>
              </div>
            )}
          </div>

          <h2 className="text-xl font-semibold text-gray-100 mb-4">Question Review</h2>
          <div className="space-y-4 mb-8">
            {assessment?.questions?.map((q, idx) => {
              const answer = answers[idx];
              const isCorrect = answer?.correct;
              return (
                <div
                  key={idx}
                  className={`bg-gray-800 border rounded-xl p-4 ${
                    isCorrect ? 'border-green-700/50' : 'border-red-700/50'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div
                      className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0 ${
                        isCorrect
                          ? 'bg-green-900/30 text-green-400'
                          : 'bg-red-900/30 text-red-400'
                      }`}
                    >
                      {isCorrect ? '✓' : '✗'}
                    </div>
                    <div className="flex-1">
                      <div className="text-gray-100 font-medium">{q.question}</div>
                      {answer && (
                        <div className="mt-2 text-sm">
                          <span className="text-gray-400">Your answer: </span>
                          <span className={isCorrect ? 'text-green-400' : 'text-red-400'}>
                            {q.options?.[answer.answerIndex] ?? `Option ${answer.answerIndex + 1}`}
                          </span>
                        </div>
                      )}
                      {!isCorrect && answer?.correctAnswerIndex != null && (
                        <div className="mt-1 text-sm">
                          <span className="text-gray-400">Correct answer: </span>
                          <span className="text-green-400">
                            {q.options?.[answer.correctAnswerIndex] ??
                              `Option ${answer.correctAnswerIndex + 1}`}
                          </span>
                        </div>
                      )}
                      {answer?.explanation && (
                        <div className="mt-2 text-sm text-gray-400 italic bg-gray-700/30 rounded-lg px-3 py-2">
                          {answer.explanation}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="flex justify-center gap-4">
            <button
              onClick={resetAssessment}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl transition-colors"
            >
              Take Another Assessment
            </button>
          </div>
        </div>
      </div>
    );
  }

  return null;
}
