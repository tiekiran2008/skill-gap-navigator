import { useState, useEffect, useCallback } from "react";

const CATEGORIES = {
  technical: { label: "Technical", color: "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30" },
  behavioral: { label: "Behavioral", color: "bg-violet-500/20 text-violet-400 border border-violet-500/30" },
  project: { label: "Project", color: "bg-amber-500/20 text-amber-400 border border-amber-500/30" },
  scenario: { label: "Scenario", color: "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30" },
};

const DIFFICULTY = {
  Beginner: "bg-green-500/20 text-green-400 border border-green-500/30",
  Intermediate: "bg-yellow-500/20 text-yellow-400 border border-yellow-500/30",
  Advanced: "bg-red-500/20 text-red-400 border border-red-500/30",
};

function getScoreColor(score) {
  if (score >= 80) return "text-green-400";
  if (score >= 60) return "text-yellow-400";
  if (score >= 40) return "text-orange-400";
  return "text-red-400";
}

function ScoreRing({ score, size = 140 }) {
  const radius = (size - 14) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth="10"
          className="text-gray-800"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth="10"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className={`${getScoreColor(score)} transition-all duration-1000 ease-out`}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`text-3xl font-bold ${getScoreColor(score)}`}>{score}</span>
        <span className="text-xs text-gray-500">/ 100</span>
      </div>
    </div>
  );
}

function ProgressBar({ current, total }) {
  const pct = total > 0 ? ((current + 1) / total) * 100 : 0;
  return (
    <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden">
      <div
        className="h-full bg-gradient-to-r from-violet-500 to-cyan-500 rounded-full transition-all duration-500"
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}

function QuestionCard({ question, index, total, answer, onAnswerChange }) {
  const cat = CATEGORIES[question.category] || CATEGORIES.technical;
  const diff = DIFFICULTY[question.difficulty] || DIFFICULTY.Beginner;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-400">
          Question {index + 1} <span className="text-gray-600">/ {total}</span>
        </span>
        <div className="flex gap-2">
          <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${cat.color}`}>
            {cat.label}
          </span>
          <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${diff}`}>
            {question.difficulty}
          </span>
        </div>
      </div>

      <h2 className="text-lg font-semibold text-gray-100 leading-relaxed">
        {question.question}
      </h2>

      {question.context && (
        <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-4">
          <p className="text-sm text-gray-400 leading-relaxed">{question.context}</p>
        </div>
      )}

      <textarea
        value={answer}
        onChange={(e) => onAnswerChange(e.target.value)}
        placeholder="Type your answer here..."
        rows={8}
        className="w-full bg-gray-900 border border-gray-700/50 rounded-xl p-4 text-gray-100 placeholder-gray-600
                   focus:outline-none focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500/50
                   resize-none transition-all duration-200"
      />

      <div className="flex items-center justify-between text-xs text-gray-600">
        <span>{answer.length} characters</span>
        {answer.length < 20 && answer.length > 0 && (
          <span className="text-yellow-500/70">Consider providing a more detailed answer</span>
        )}
      </div>
    </div>
  );
}

function ReviewCard({ q, i }) {
  const cat = CATEGORIES[q.category] || CATEGORIES.technical;
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-5 space-y-3">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs text-gray-500 font-medium">Q{i + 1}</span>
            <span className={`px-2 py-0.5 rounded-full text-[10px] font-medium ${cat.color}`}>
              {cat.label}
            </span>
          </div>
          <p className="text-sm text-gray-200 font-medium">{q.question}</p>
        </div>
        <span className={`text-xl font-bold whitespace-nowrap ${getScoreColor(q.score)}`}>
          {q.score}
        </span>
      </div>

      <button
        onClick={() => setExpanded(!expanded)}
        className="text-xs text-violet-400 hover:text-violet-300 transition-colors"
      >
        {expanded ? "Hide details" : "Show details"}
      </button>

      {expanded && (
        <div className="space-y-3 pt-2 border-t border-gray-800">
          <div>
            <p className="text-[11px] uppercase tracking-wider text-gray-500 mb-1">Your Answer</p>
            <p className="text-sm text-gray-300 bg-gray-800/50 rounded-lg p-3 whitespace-pre-wrap">
              {q.user_answer || <span className="text-gray-600 italic">No answer provided</span>}
            </p>
          </div>
          <div>
            <p className="text-[11px] uppercase tracking-wider text-gray-500 mb-1">Key Concepts</p>
            <p className="text-sm text-gray-300 bg-gray-800/50 rounded-lg p-3 whitespace-pre-wrap">
              {q.expected_concepts?.join(', ') || q.correct_answer || <span className="text-gray-600 italic">N/A</span>}
            </p>
          </div>
          <div>
            <p className="text-[11px] uppercase tracking-wider text-gray-500 mb-1">Feedback</p>
            <p className="text-sm text-gray-300 bg-gray-800/50 rounded-lg p-3 whitespace-pre-wrap">
              {q.feedback || <span className="text-gray-600 italic">No feedback</span>}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default function MockInterview({ interviewData, onNavigate }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const questions = interviewData?.questions || [];
  const interviewId = interviewData?.interview_id || interviewData?.id;
  const currentQ = questions[currentIndex];

  const handleAnswerChange = useCallback((value) => {
    setAnswers((prev) => ({ ...prev, [questions[currentIndex]?.id]: value }));
  }, [currentIndex, questions]);

  const submitAnswer = useCallback(
    async (questionId, answer) => {
      if (!interviewId || !questionId) return;
      try {
        await fetch(`/api/v1/interview/${interviewId}/answer`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question_id: questionId, answer }),
        });
      } catch {
        // Non-blocking; best-effort submission per answer
      }
    },
    [interviewId]
  );

  const completeInterview = useCallback(async () => {
    if (!interviewId) return;
    setLoading(true);
    setError(null);
    try {
      // Submit all answers
      const entries = Object.entries(answers);
      for (const [qid, ans] of entries) {
        await submitAnswer(qid, ans);
      }

      // Mark complete
      const res = await fetch(`/api/v1/interview/${interviewId}/complete`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      if (!res.ok) throw new Error("Failed to complete interview");

      // Fetch full results
      const resultRes = await fetch(`/api/v1/interview/${interviewId}`);
      if (!resultRes.ok) throw new Error("Failed to fetch results");
      const data = await resultRes.json();
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [interviewId, answers, submitAnswer]);

  const addWeakTopicsToRoadmap = useCallback(async () => {
    if (!results?.weak_areas?.length) return;
    try {
      await fetch("/api/v1/roadmap/add-topics", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topics: results.weak_areas.map((w) => w.topic || w) }),
      });
    } catch {
      // non-critical
    }
  }, [results]);

  useEffect(() => {
    if (!currentQ || !interviewId) return;
    const value = answers[currentQ.id] || "";
    if (value.length > 0) {
      submitAnswer(currentQ.id, value);
    }
  }, [currentIndex]); // eslint-disable-line react-hooks/exhaustive-deps

  // ---------- RESULTS VIEW ----------
  if (results) {
    const qResults = results.question_results || results.questions || [];
    const overallScore = results.overall_score ?? results.score ?? 0;
    const strongAreas = results.strong_areas || [];
    const weakAreas = results.weak_areas || [];
    const reviewTopics = results.review_topics || results.topics_to_review || [];

    return (
      <div className="min-h-screen bg-gray-950 text-gray-100">
        <div className="max-w-4xl mx-auto px-4 py-8 space-y-10">
          {/* Header */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => onNavigate?.("interview-prep")}
              className="p-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-gray-200 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <h1 className="text-2xl font-bold text-gray-100">Interview Results</h1>
          </div>

          {/* Overall Score */}
          <div className="flex flex-col items-center bg-gray-900/50 border border-gray-800 rounded-2xl p-8">
            <p className="text-sm text-gray-400 mb-4 uppercase tracking-wider">Overall Score</p>
            <ScoreRing score={overallScore} size={160} />
            <p className={`mt-4 text-lg font-semibold ${getScoreColor(overallScore)}`}>
              {overallScore >= 80
                ? "Excellent work!"
                : overallScore >= 60
                ? "Good effort!"
                : overallScore >= 40
                ? "Room for improvement"
                : "Keep practicing!"}
            </p>
          </div>

          {/* Category Breakdown */}
          {results.category_scores && (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {Object.entries(results.category_scores).map(([cat, score]) => (
                <div
                  key={cat}
                  className="bg-gray-900/50 border border-gray-800 rounded-xl p-5 text-center space-y-2"
                >
                  <p className="text-xs uppercase tracking-wider text-gray-500">
                    {CATEGORIES[cat]?.label || cat}
                  </p>
                  <p className={`text-2xl font-bold ${getScoreColor(score)}`}>{score}</p>
                </div>
              ))}
            </div>
          )}

          {/* Strong / Weak / Review */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {strongAreas.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-green-400 uppercase tracking-wider">
                  Strong Areas
                </h3>
                <div className="flex flex-wrap gap-2">
                  {strongAreas.map((a, i) => (
                    <span
                      key={i}
                      className="px-3 py-1 rounded-full text-xs font-medium bg-green-500/15 text-green-400 border border-green-500/20"
                    >
                      {typeof a === "string" ? a : a.topic}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {weakAreas.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-red-400 uppercase tracking-wider">
                  Weak Areas
                </h3>
                <div className="flex flex-wrap gap-2">
                  {weakAreas.map((a, i) => (
                    <span
                      key={i}
                      className="px-3 py-1 rounded-full text-xs font-medium bg-red-500/15 text-red-400 border border-red-500/20"
                    >
                      {typeof a === "string" ? a : a.topic}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {reviewTopics.length > 0 && (
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-yellow-400 uppercase tracking-wider">
                  Topics to Review
                </h3>
                <div className="flex flex-wrap gap-2">
                  {reviewTopics.map((a, i) => (
                    <span
                      key={i}
                      className="px-3 py-1 rounded-full text-xs font-medium bg-yellow-500/15 text-yellow-400 border border-yellow-500/20"
                    >
                      {typeof a === "string" ? a : a.topic}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Question Review */}
          {qResults.length > 0 && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-200">Question-by-Question Review</h3>
              <div className="space-y-3">
                {qResults.map((q, i) => (
                  <ReviewCard key={i} q={q} i={i} />
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3 pt-4 border-t border-gray-800">
            <button
              onClick={addWeakTopicsToRoadmap}
              className="flex-1 px-5 py-3 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-medium text-sm transition-colors"
            >
              Add Weak Topics to Roadmap
            </button>
            <button
              onClick={() => onNavigate?.("mock-interview", { restart: true })}
              className="flex-1 px-5 py-3 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-200 font-medium text-sm border border-gray-700 transition-colors"
            >
              Take Another Interview
            </button>
            <button
              onClick={() => onNavigate?.("interview-prep")}
              className="flex-1 px-5 py-3 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-200 font-medium text-sm border border-gray-700 transition-colors"
            >
              Back to Interview Prep
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ---------- IN PROGRESS VIEW ----------
  if (!currentQ) {
    return (
      <div className="min-h-screen bg-gray-950 text-gray-100 flex items-center justify-center">
        <div className="text-center space-y-4">
          <p className="text-gray-400">No questions available.</p>
          <button
            onClick={() => onNavigate?.("interview-prep")}
            className="px-4 py-2 rounded-lg bg-violet-600 hover:bg-violet-500 text-white text-sm transition-colors"
          >
            Back to Interview Prep
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">
        {/* Top Bar */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigate?.("interview-prep")}
            className="p-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-gray-200 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <div className="flex-1">
            <h1 className="text-xl font-bold text-gray-100">Mock Interview</h1>
          </div>
        </div>

        {/* Progress */}
        <div className="space-y-2">
          <ProgressBar current={currentIndex} total={questions.length} />
          <p className="text-xs text-gray-500 text-right">
            {Object.keys(answers).length} / {questions.length} answered
          </p>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 text-sm text-red-400">
            {error}
          </div>
        )}

        {/* Question Card */}
        <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-6">
          <QuestionCard
            question={currentQ}
            index={currentIndex}
            total={questions.length}
            answer={answers[currentQ.id] || ""}
            onAnswerChange={handleAnswerChange}
          />
        </div>

        {/* Navigation */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => setCurrentIndex((i) => Math.max(0, i - 1))}
            disabled={currentIndex === 0}
            className="px-5 py-2.5 rounded-xl bg-gray-800 hover:bg-gray-700 disabled:opacity-30 disabled:cursor-not-allowed
                       text-gray-300 font-medium text-sm border border-gray-700 transition-colors"
          >
            Previous
          </button>

          <div className="flex-1" />

          {currentIndex < questions.length - 1 ? (
            <button
              onClick={() => setCurrentIndex((i) => Math.min(questions.length - 1, i + 1))}
              className="px-5 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white font-medium text-sm transition-colors"
            >
              Next
            </button>
          ) : (
            <button
              onClick={completeInterview}
              disabled={loading}
              className="px-6 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-cyan-600 hover:from-violet-500 hover:to-cyan-500
                         text-white font-semibold text-sm disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                  </svg>
                  Submitting...
                </span>
              ) : (
                "Submit Answer"
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
