import { useState, useEffect, useRef } from 'react'
import { useLocation } from 'react-router-dom'
import { RefreshCw, Bell, Lock, Unlock, X, Eye, EyeOff } from 'lucide-react'
import axios from 'axios'

const STORAGE_KEY = 'ai_pulse_sync_key'

const PAGE_TITLES = {
  '/': 'Dashboard',
  '/news': 'AI News',
  '/research': 'Research & Papers',
  '/courses': 'Courses',
  '/github': 'GitHub Repositories',
  '/agents': 'AI Agents & Tools',
  '/trends': 'Trends',
  '/videos': 'Videos',
}

const FETCH_ENDPOINTS = {
  '/news': '/api/news/fetch',
  '/research': '/api/research/fetch',
  '/github': '/api/github/fetch',
  '/agents': '/api/agents/fetch',
  '/courses': '/api/courses/fetch',
  '/trends': '/api/trends/fetch',
}

function KeyModal({ onClose, onUnlock }) {
  const [key, setKey] = useState('')
  const [showKey, setShowKey] = useState(false)
  const [error, setError] = useState('')
  const inputRef = useRef(null)

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!key.trim()) return
    setError('')
    try {
      // Validate the key by hitting a protected endpoint
      await axios.post('/api/trends/fetch', null, {
        headers: { 'x-sync-key': key.trim() },
      })
      localStorage.setItem(STORAGE_KEY, key.trim())
      onUnlock()
    } catch (err) {
      if (err.response?.status === 403) {
        setError('Wrong key — access denied.')
      } else if (err.response?.status === 503) {
        setError('Sync key not configured on the server.')
      } else {
        // Any other error means key was accepted (e.g. network issues post-auth)
        localStorage.setItem(STORAGE_KEY, key.trim())
        onUnlock()
      }
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-bg-card border border-border rounded-2xl p-6 w-full max-w-sm mx-4 shadow-2xl animate-slide-up">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-500 hover:text-white transition-colors"
        >
          <X size={16} />
        </button>

        <div className="flex items-center gap-3 mb-5">
          <div className="w-10 h-10 rounded-xl bg-accent-purple/20 border border-accent-purple/30 flex items-center justify-center">
            <Lock size={18} className="text-accent-purple" />
          </div>
          <div>
            <div className="text-white font-semibold text-sm">Admin Access</div>
            <div className="text-slate-500 text-xs">Enter your sync key to unlock</div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="relative">
            <input
              ref={inputRef}
              type={showKey ? 'text' : 'password'}
              value={key}
              onChange={e => { setKey(e.target.value); setError('') }}
              placeholder="Sync secret key"
              className="w-full px-3 py-2.5 pr-10 bg-bg-hover border border-border rounded-lg text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-accent-purple transition-colors"
            />
            <button
              type="button"
              onClick={() => setShowKey(v => !v)}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
            >
              {showKey ? <EyeOff size={14} /> : <Eye size={14} />}
            </button>
          </div>

          {error && (
            <p className="text-red-400 text-xs flex items-center gap-1.5 animate-fade-in">
              <X size={11} /> {error}
            </p>
          )}

          <button
            type="submit"
            disabled={!key.trim()}
            className="w-full btn-primary disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Unlock Sync
          </button>
        </form>

        <p className="text-slate-600 text-[10px] text-center mt-4">
          Key is stored in browser localStorage only
        </p>
      </div>
    </div>
  )
}

export default function Topbar() {
  const location = useLocation()
  const [syncing, setSyncing] = useState(false)
  const [syncMsg, setSyncMsg] = useState({ text: '', type: 'success' })
  const [showModal, setShowModal] = useState(false)
  const [syncKey, setSyncKey] = useState(() => localStorage.getItem(STORAGE_KEY) || '')

  const isUnlocked = Boolean(syncKey)
  const title = PAGE_TITLES[location.pathname] || 'AI Pulse'
  const endpoint = FETCH_ENDPOINTS[location.pathname]

  const handleSync = async () => {
    if (!endpoint || !syncKey) return
    setSyncing(true)
    setSyncMsg({ text: '', type: 'success' })
    try {
      const res = await axios.post(endpoint, null, {
        headers: { 'x-sync-key': syncKey },
      })
      setSyncMsg({ text: `+${res.data.fetched} new items`, type: 'success' })
      setTimeout(() => setSyncMsg({ text: '', type: 'success' }), 3000)
    } catch (err) {
      if (err.response?.status === 403) {
        // Key was revoked or changed — lock the UI
        localStorage.removeItem(STORAGE_KEY)
        setSyncKey('')
        setSyncMsg({ text: 'Key invalid — locked', type: 'error' })
      } else {
        setSyncMsg({ text: 'Sync failed', type: 'error' })
      }
      setTimeout(() => setSyncMsg({ text: '', type: 'success' }), 3000)
    } finally {
      setSyncing(false)
    }
  }

  const handleLock = () => {
    localStorage.removeItem(STORAGE_KEY)
    setSyncKey('')
  }

  const handleUnlock = () => {
    setSyncKey(localStorage.getItem(STORAGE_KEY) || '')
    setShowModal(false)
  }

  return (
    <>
      <header className="h-14 bg-bg-secondary border-b border-border flex items-center px-6 gap-4 shrink-0">
        <div className="flex-1">
          <h1 className="text-white font-semibold text-base">{title}</h1>
        </div>

        <div className="flex items-center gap-2">
          {syncMsg.text && (
            <span className={`text-xs px-2.5 py-1 rounded-full animate-fade-in ${
              syncMsg.type === 'error'
                ? 'text-red-400 bg-red-500/10'
                : 'text-accent-green bg-accent-green/10'
            }`}>
              {syncMsg.text}
            </span>
          )}

          {/* Sync button — only visible when unlocked and on a syncable page */}
          {isUnlocked && endpoint && (
            <button
              onClick={handleSync}
              disabled={syncing}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-300 hover:text-white bg-bg-hover hover:bg-border-light border border-border rounded-lg transition-all duration-150 disabled:opacity-50"
            >
              <RefreshCw size={13} className={syncing ? 'animate-spin' : ''} />
              Sync
            </button>
          )}

          {/* Lock / Unlock toggle */}
          {isUnlocked ? (
            <button
              onClick={handleLock}
              title="Lock sync (sign out)"
              className="w-8 h-8 flex items-center justify-center rounded-lg text-accent-green hover:text-white hover:bg-bg-hover transition-colors"
            >
              <Unlock size={15} />
            </button>
          ) : (
            <button
              onClick={() => setShowModal(true)}
              title="Admin unlock"
              className="w-8 h-8 flex items-center justify-center rounded-lg text-slate-500 hover:text-slate-300 hover:bg-bg-hover transition-colors"
            >
              <Lock size={15} />
            </button>
          )}

          <button className="w-8 h-8 flex items-center justify-center rounded-lg text-slate-400 hover:text-white hover:bg-bg-hover transition-colors">
            <Bell size={16} />
          </button>
        </div>
      </header>

      {showModal && (
        <KeyModal onClose={() => setShowModal(false)} onUnlock={handleUnlock} />
      )}
    </>
  )
}
