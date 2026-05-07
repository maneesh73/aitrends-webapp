import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import {
  Newspaper, FlaskConical, GraduationCap, Github,
  Bot, TrendingUp, Youtube, ArrowRight, Zap, Star
} from 'lucide-react'

const SECTIONS = [
  { to: '/news', icon: Newspaper, label: 'AI News', color: 'from-blue-600 to-blue-800', desc: 'Latest AI headlines from top sources' },
  { to: '/research', icon: FlaskConical, label: 'Research', color: 'from-purple-600 to-purple-800', desc: 'arXiv papers & white papers' },
  { to: '/courses', icon: GraduationCap, label: 'Courses', color: 'from-green-600 to-green-800', desc: 'Curated AI learning resources' },
  { to: '/github', icon: Github, label: 'GitHub', color: 'from-gray-600 to-gray-800', desc: 'Trending AI repositories' },
  { to: '/agents', icon: Bot, label: 'Agents & Tools', color: 'from-orange-600 to-orange-800', desc: 'AI frameworks and tools' },
  { to: '/trends', icon: TrendingUp, label: 'Trends', color: 'from-pink-600 to-pink-800', desc: 'Hot topics in AI right now' },
  { to: '/videos', icon: Youtube, label: 'Videos', color: 'from-red-600 to-red-800', desc: 'YouTube AI tutorials & talks' },
]

export default function Home() {
  const [stats, setStats] = useState(null)
  const [seeding, setSeeding] = useState(false)
  const [seedDone, setSeedDone] = useState(false)

  useEffect(() => {
    axios.get('/api/trends/stats').then(r => setStats(r.data)).catch(() => {})
  }, [seedDone])

  const handleSeedAll = async () => {
    setSeeding(true)
    try {
      await axios.post('/api/seed-all')
      setSeedDone(true)
    } catch {}
    setSeeding(false)
  }

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-fade-in">
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-accent-purple/20 via-bg-card to-accent-cyan/10 border border-border p-8">
        <div className="absolute top-0 right-0 w-64 h-64 bg-accent-purple/5 rounded-full -translate-y-1/2 translate-x-1/2 blur-3xl" />
        <div className="relative">
          <div className="flex items-center gap-2 mb-3">
            <div className="badge bg-accent-purple/20 text-accent-purple border border-accent-purple/30">
              <Zap size={10} /> Live Updates
            </div>
          </div>
          <h1 className="text-4xl font-bold text-white mb-3">
            Your AI Intelligence Hub
          </h1>
          <p className="text-slate-400 text-lg max-w-xl mb-6">
            Stay ahead of the curve with real-time AI news, research papers, trending GitHub repos, courses, and the hottest tools.
          </p>
          {!seedDone ? (
            <button
              onClick={handleSeedAll}
              disabled={seeding}
              className="btn-primary flex items-center gap-2"
            >
              {seeding ? 'Loading data...' : 'Initialize & Load All Data'}
              <ArrowRight size={14} />
            </button>
          ) : (
            <div className="text-sm text-accent-green flex items-center gap-1.5">
              <Star size={14} /> Data loaded! Explore the sections below.
            </div>
          )}
        </div>
      </div>

      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { label: 'News Articles', value: stats.articles, color: 'text-blue-400' },
            { label: 'GitHub Repos', value: stats.repositories, color: 'text-slate-300' },
            { label: 'Research Papers', value: stats.papers, color: 'text-purple-400' },
            { label: 'Trend Topics', value: stats.trends, color: 'text-pink-400' },
          ].map(s => (
            <div key={s.label} className="card text-center">
              <div className={`text-3xl font-bold ${s.color}`}>{s.value}</div>
              <div className="text-slate-500 text-xs mt-1">{s.label}</div>
            </div>
          ))}
        </div>
      )}

      <div>
        <h2 className="text-lg font-semibold text-white mb-4">Explore Sections</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {SECTIONS.map(({ to, icon: Icon, label, color, desc }) => (
            <Link
              key={to}
              to={to}
              className="card group flex items-start gap-4 hover:scale-[1.01] transition-transform"
            >
              <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${color} flex items-center justify-center shrink-0`}>
                <Icon size={18} className="text-white" />
              </div>
              <div>
                <div className="text-white font-semibold text-sm group-hover:text-accent-cyan transition-colors">{label}</div>
                <div className="text-slate-500 text-xs mt-0.5">{desc}</div>
              </div>
              <ArrowRight size={14} className="ml-auto text-slate-600 group-hover:text-slate-400 mt-1 shrink-0" />
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}
