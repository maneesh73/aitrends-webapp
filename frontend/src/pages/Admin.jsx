import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'
import {
  Newspaper, Github, FlaskConical, GraduationCap, Bot,
  Youtube, TrendingUp, Play, ChevronDown, ChevronUp,
  Clock, CheckCircle, XCircle, Settings, Lock, RefreshCw
} from 'lucide-react'

const JOB_ICONS = {
  news: Newspaper,
  github: Github,
  research: FlaskConical,
  courses: GraduationCap,
  agents: Bot,
  videos: Youtube,
  trends: TrendingUp,
}

const SOURCE_TYPE_COLORS = {
  'RSS': 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  'Google News': 'bg-green-500/10 text-green-400 border-green-500/20',
  'Reddit RSS': 'bg-orange-500/10 text-orange-400 border-orange-500/20',
  'API': 'bg-purple-500/10 text-purple-400 border-purple-500/20',
  'GitHub API': 'bg-slate-500/10 text-slate-400 border-slate-500/20',
  'arXiv API': 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
  'YouTube API': 'bg-red-500/10 text-red-400 border-red-500/20',
  'HuggingFace API': 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  'Curated': 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
}

const CRON_PRESETS = [
  { label: 'Every hour', value: '0 * * * *' },
  { label: 'Every 3 hours', value: '0 */3 * * *' },
  { label: 'Every 6 hours', value: '0 */6 * * *' },
  { label: 'Every 12 hours', value: '0 */12 * * *' },
  { label: 'Every 24 hours', value: '0 0 * * *' },
  { label: 'Weekly (Sunday)', value: '0 0 * * 0' },
  { label: 'Custom', value: '__custom__' },
]

function timeAgo(dateStr) {
  if (!dateStr) return 'Never'
  const diff = Date.now() - new Date(dateStr).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1) return 'just now'
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}

function formatTime(dateStr) {
  if (!dateStr) return '—'
  return new Date(dateStr).toLocaleString()
}

function Toggle({ checked, onChange }) {
  return (
    <button
      onClick={() => onChange(!checked)}
      className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${checked ? 'bg-accent-purple' : 'bg-slate-700'}`}
    >
      <span className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform ${checked ? 'translate-x-5' : 'translate-x-1'}`} />
    </button>
  )
}

function JobCard({ job, apiKey, onUpdated }) {
  const Icon = JOB_ICONS[job.id] || Settings
  const [showSources, setShowSources] = useState(false)
  const [enabled, setEnabled] = useState(job.enabled)
  const [cronValue, setCronValue] = useState(
    CRON_PRESETS.find(p => p.value === job.cron_expr) ? job.cron_expr : '__custom__'
  )
  const [customCron, setCustomCron] = useState(
    CRON_PRESETS.find(p => p.value === job.cron_expr) ? '' : job.cron_expr
  )
  const [saving, setSaving] = useState(false)
  const [running, setRunning] = useState(false)
  const [saveError, setSaveError] = useState(null)

  const effectiveCron = cronValue === '__custom__' ? customCron : cronValue

  const handleSave = async () => {
    setSaving(true)
    setSaveError(null)
    try {
      const res = await axios.put(`/api/admin/jobs/${job.id}`, {
        cron_expr: effectiveCron,
        enabled,
      }, { headers: { 'x-sync-key': apiKey } })
      onUpdated(res.data)
    } catch (e) {
      setSaveError(e.response?.data?.detail || 'Save failed')
    } finally {
      setSaving(false)
    }
  }

  const handleRunNow = async () => {
    setRunning(true)
    try {
      await axios.post(`/api/admin/jobs/${job.id}/run`, {}, {
        headers: { 'x-sync-key': apiKey },
      })
      setTimeout(() => { onUpdated(null); setRunning(false) }, 3000)
    } catch {
      setRunning(false)
    }
  }

  const isDirty = enabled !== job.enabled || effectiveCron !== job.cron_expr

  return (
    <div className="card flex flex-col gap-4">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-bg-hover flex items-center justify-center shrink-0">
            <Icon size={18} className="text-slate-400" />
          </div>
          <div>
            <div className="text-white font-semibold text-sm">{job.name}</div>
            <div className="text-slate-500 text-xs leading-snug mt-0.5">{job.description}</div>
          </div>
        </div>
        <Toggle checked={enabled} onChange={setEnabled} />
      </div>

      <div className="flex flex-col gap-2">
        <label className="text-xs text-slate-500 font-medium">Schedule</label>
        <select
          value={cronValue}
          onChange={e => setCronValue(e.target.value)}
          className="w-full bg-bg-hover border border-border rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-slate-500"
        >
          {CRON_PRESETS.map(p => (
            <option key={p.value} value={p.value}>{p.label}</option>
          ))}
        </select>
        {cronValue === '__custom__' && (
          <input
            type="text"
            value={customCron}
            onChange={e => setCustomCron(e.target.value)}
            placeholder="e.g. 0 */4 * * *"
            className="w-full bg-bg-hover border border-border rounded-lg px-3 py-1.5 text-sm text-white font-mono focus:outline-none focus:border-slate-500"
          />
        )}
      </div>

      <div className="grid grid-cols-2 gap-3 text-xs">
        <div>
          <div className="text-slate-600 mb-0.5">Last run</div>
          <div className="flex items-center gap-1.5">
            {job.last_run_status === 'ok' && <CheckCircle size={11} className="text-green-400 shrink-0" />}
            {job.last_run_status === 'error' && <XCircle size={11} className="text-red-400 shrink-0" />}
            {!job.last_run_status && <Clock size={11} className="text-slate-600 shrink-0" />}
            <span className="text-slate-400" title={formatTime(job.last_run_at)}>{timeAgo(job.last_run_at)}</span>
          </div>
          {job.last_run_status === 'error' && job.last_run_message && (
            <div className="text-red-400 text-[10px] mt-0.5 line-clamp-2">{job.last_run_message}</div>
          )}
          {job.last_run_status === 'ok' && job.last_run_message && (
            <div className="text-slate-600 text-[10px] mt-0.5">{job.last_run_message}</div>
          )}
        </div>
        <div>
          <div className="text-slate-600 mb-0.5">Next run</div>
          <div className="text-slate-400">
            {job.enabled && job.next_run_at ? timeAgo(job.next_run_at).replace(' ago', '') : job.enabled ? '—' : 'Disabled'}
          </div>
          {job.enabled && job.next_run_at && (
            <div className="text-slate-600 text-[10px] mt-0.5">{formatTime(job.next_run_at)}</div>
          )}
        </div>
      </div>

      <button
        onClick={() => setShowSources(v => !v)}
        className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-400 transition-colors"
      >
        {showSources ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
        {job.sources.length} sources
      </button>

      {showSources && (
        <div className="flex flex-wrap gap-1.5 pt-1 border-t border-border">
          {job.sources.map((src, i) => {
            const colorClass = SOURCE_TYPE_COLORS[src.type] || 'bg-slate-500/10 text-slate-400 border-slate-500/20'
            return (
              <div key={i} className="flex flex-col gap-0.5">
                <span className={`badge border text-[10px] ${colorClass}`}>
                  <span className="opacity-60 mr-1">{src.type}</span>{src.name}
                </span>
                {src.note && <span className="text-[9px] text-amber-500 pl-1">{src.note}</span>}
              </div>
            )
          })}
        </div>
      )}

      {saveError && (
        <div className="text-red-400 text-xs bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
          {saveError}
        </div>
      )}

      <div className="flex gap-2 pt-1 border-t border-border">
        <button
          onClick={handleSave}
          disabled={saving || !isDirty}
          className={`flex-1 py-1.5 rounded-lg text-xs font-medium transition-colors ${
            isDirty
              ? 'bg-accent-purple text-white hover:opacity-90'
              : 'bg-bg-hover text-slate-600 cursor-not-allowed'
          }`}
        >
          {saving ? 'Saving…' : 'Save schedule'}
        </button>
        <button
          onClick={handleRunNow}
          disabled={running}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-bg-hover text-slate-400 hover:text-white hover:bg-slate-700 transition-colors disabled:opacity-50"
        >
          {running ? <RefreshCw size={11} className="animate-spin" /> : <Play size={11} />}
          {running ? 'Running…' : 'Run now'}
        </button>
      </div>
    </div>
  )
}

export default function Admin() {
  const [apiKey, setApiKey] = useState(() => localStorage.getItem('admin_key') || '')
  const [keyInput, setKeyInput] = useState('')
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(false)
  const [authError, setAuthError] = useState(null)
  const [authed, setAuthed] = useState(false)

  const fetchJobs = useCallback(async (key) => {
    setLoading(true)
    setAuthError(null)
    try {
      const res = await axios.get('/api/admin/jobs', { headers: { 'x-sync-key': key } })
      setJobs(res.data)
      setAuthed(true)
    } catch (e) {
      if (e.response?.status === 403) {
        setAuthError('Invalid admin key')
        setAuthed(false)
      } else {
        setAuthError('Failed to load jobs')
      }
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (apiKey) fetchJobs(apiKey)
  }, [apiKey, fetchJobs])

  const handleAuth = (e) => {
    e.preventDefault()
    localStorage.setItem('admin_key', keyInput)
    setApiKey(keyInput)
  }

  const handleJobUpdated = (updatedJob) => {
    if (updatedJob) {
      setJobs(prev => prev.map(j => j.id === updatedJob.id ? updatedJob : j))
    } else {
      fetchJobs(apiKey)
    }
  }

  if (!authed) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="card w-full max-w-sm flex flex-col gap-5">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-bg-hover flex items-center justify-center">
              <Lock size={18} className="text-slate-400" />
            </div>
            <div>
              <div className="text-white font-semibold">Admin Access</div>
              <div className="text-slate-500 text-xs">Enter your sync secret key</div>
            </div>
          </div>
          <form onSubmit={handleAuth} className="flex flex-col gap-3">
            <input
              type="password"
              value={keyInput}
              onChange={e => setKeyInput(e.target.value)}
              placeholder="SYNC_SECRET_KEY"
              className="w-full bg-bg-hover border border-border rounded-lg px-3 py-2 text-sm text-white font-mono focus:outline-none focus:border-slate-500"
              autoFocus
            />
            {authError && <div className="text-red-400 text-xs">{authError}</div>}
            <button
              type="submit"
              disabled={!keyInput || loading}
              className="py-2 rounded-lg text-sm font-medium bg-accent-purple text-white hover:opacity-90 disabled:opacity-50 transition-opacity"
            >
              {loading ? 'Verifying…' : 'Access Admin'}
            </button>
          </form>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-white font-bold text-xl">Sync Scheduler</h1>
          <p className="text-slate-500 text-sm mt-0.5">Configure automated data sync jobs and view their sources</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => fetchJobs(apiKey)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs text-slate-400 hover:text-white bg-bg-hover hover:bg-slate-700 transition-colors"
          >
            <RefreshCw size={12} /> Refresh
          </button>
          <button
            onClick={() => { localStorage.removeItem('admin_key'); setApiKey(''); setAuthed(false); setJobs([]) }}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs text-slate-400 hover:text-red-400 bg-bg-hover transition-colors"
          >
            <Lock size={12} /> Lock
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-slate-500 text-sm text-center py-12">Loading jobs…</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {jobs.map(job => (
            <JobCard key={job.id} job={job} apiKey={apiKey} onUpdated={handleJobUpdated} />
          ))}
        </div>
      )}
    </div>
  )
}
