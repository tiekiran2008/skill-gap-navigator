import { useState } from 'react'
import { useApp } from '../context/AppContext'

const API = '/api'

export default function ResumeAnalyzer() {
  const { skills, setSkills, setError } = useApp()
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [manualSkill, setManualSkill] = useState('')
  const [uploadResult, setUploadResult] = useState(null)

  const handleUpload = async () => {
    if (!file) return
    setUploading(true)
    setError('')
    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await fetch(`${API}/v1/resume/analyze`, { method: 'POST', body: formData })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Upload failed')
      }
      const data = await res.json()
      setSkills(data.skills)
      setUploadResult(data)
    } catch (e) {
      setError(e.message)
    } finally {
      setUploading(false)
    }
  }

  const addManualSkill = () => {
    const s = manualSkill.trim()
    if (s && !skills.includes(s)) {
      const updated = [...skills, s]
      setSkills(updated)
      setManualSkill('')
    }
  }

  const removeSkill = (idx) => {
    setSkills(skills.filter((_, i) => i !== idx))
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold mb-1">Resume Analyzer</h1>
        <p className="text-sm text-gray-500">Upload your resume or add skills manually</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Section */}
        <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-6 space-y-5">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">PDF Upload</h2>
          <div className="border-2 border-dashed border-gray-700 rounded-xl p-8 text-center hover:border-violet-500/40 transition-colors">
            <input
              type="file"
              accept=".pdf"
              onChange={(e) => setFile(e.target.files[0])}
              className="hidden"
              id="file-upload"
            />
            <label htmlFor="file-upload" className="cursor-pointer">
              <div className="w-14 h-14 mx-auto rounded-2xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center mb-3">
                <svg className="w-7 h-7 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                </svg>
              </div>
              <p className="text-sm text-gray-300 mb-1">
                {file ? file.name : 'Click to select PDF'}
              </p>
              <p className="text-[11px] text-gray-500">Supports .pdf files only</p>
            </label>
          </div>
          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="w-full py-2.5 rounded-xl font-medium bg-violet-600 hover:bg-violet-500 disabled:bg-gray-700 disabled:text-gray-500 transition-colors text-sm"
          >
            {uploading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Extracting Skills...
              </span>
            ) : 'Upload & Extract'}
          </button>
          {uploadResult && (
            <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-3 text-sm text-emerald-300">
              Extracted {uploadResult.skills_count} skills from {uploadResult.filename}
            </div>
          )}
        </div>

        {/* Manual Add Section */}
        <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-6 space-y-5">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Add Skills Manually</h2>
          <div className="flex gap-2">
            <input
              type="text"
              value={manualSkill}
              onChange={(e) => setManualSkill(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && addManualSkill()}
              placeholder="Type a skill..."
              className="flex-1 bg-gray-800 border border-gray-700 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:border-violet-500 transition-colors"
            />
            <button
              onClick={addManualSkill}
              disabled={!manualSkill.trim()}
              className="px-4 py-2.5 rounded-xl bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 disabled:text-gray-600 transition-colors text-sm font-medium"
            >
              Add
            </button>
          </div>
          <div>
            <p className="text-[11px] text-gray-500 uppercase tracking-wider mb-2">Quick Add</p>
            <div className="flex flex-wrap gap-1.5">
              {['Python', 'JavaScript', 'React', 'Node.js', 'SQL', 'Java', 'Docker', 'Git', 'Machine Learning', 'AWS'].map(s => (
                <button
                  key={s}
                  onClick={() => { if (!skills.includes(s)) { const updated = [...skills, s]; setSkills(updated) } }}
                  disabled={skills.includes(s)}
                  className="px-2.5 py-1 rounded-lg bg-gray-800 border border-gray-700 text-[11px] text-gray-400 hover:border-violet-500/40 hover:text-violet-300 disabled:opacity-30 transition-all"
                >
                  + {s}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Extracted Skills List */}
      <div className="bg-gray-900/80 backdrop-blur border border-gray-800 rounded-2xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">
            Your Skills <span className="text-violet-400">({skills.length})</span>
          </h2>
          {skills.length > 0 && (
            <button
              onClick={() => setSkills([])}
              className="text-xs text-gray-500 hover:text-red-400 transition-colors"
            >
              Clear all
            </button>
          )}
        </div>
        {skills.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {skills.map((s, i) => (
              <span
                key={i}
                className="group px-3 py-1.5 rounded-xl bg-violet-500/10 text-violet-300 border border-violet-500/20 text-xs font-medium flex items-center gap-1.5"
              >
                {s}
                <button
                  onClick={() => removeSkill(i)}
                  className="w-4 h-4 rounded-full bg-violet-500/20 text-violet-400 flex items-center justify-center text-[10px] opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-500/30 hover:text-red-300"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-500">No skills yet. Upload a resume or add skills manually.</p>
        )}
      </div>
    </div>
  )
}
