import { useState } from 'react'
import { TrendingUp, ExternalLink, Flame } from 'lucide-react'
import { usePaginatedFetch } from '../hooks/useFetch'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'

const CATEGORIES = ['', 'Models', 'Agents', 'Technique', 'Infrastructure', 'Research', 'Application', 'Tools']

const CATEGORY_COLORS = {
  Models: 'from-blue-600 to-blue-900',
  Agents: 'from-purple-600 to-purple-900',
  Technique: 'from-cyan-600 to-cyan-900',
  Infrastructure: 'from-gray-600 to-gray-900',
  Research: 'from-indigo-600 to-indigo-900',
  Application: 'from-green-600 to-green-900',
  Tools: 'from-orange-600 to-orange-900',
}

function heatColor(mentions, max) {
  const pct = mentions / max
  if (pct > 0.8) return 'text-red-400'
  if (pct > 0.6) return 'text-orange-400'
  if (pct > 0.4) return 'text-yellow-400'
  return 'text-green-400'
}

export default function Trends() {
  const [category, setCategory] = useState('')
  const { data, loading } = usePaginatedFetch('/api/trends', { category, page_size: 50 })
  const maxMentions = Math.max(...(data.items.map(t => t.mentions) || [1]))

  return (
    <div className="space-y-5 animate-fade-in">
      <div>
        <h1 className="section-title">AI Trends</h1>
        <p className="section-subtitle">Hottest topics in artificial intelligence right now</p>
        <div className="flex gap-1 flex-wrap">
          {CATEGORIES.map(c => (
            <button key={c} onClick={() => setCategory(c)}
              className={`px-3 py-1.5 text-xs rounded-lg border transition-colors ${
                category === c ? 'bg-accent-purple text-white border-accent-purple' : 'bg-bg-card text-slate-400 border-border hover:border-border-light'
              }`}>{c || 'All'}</button>
          ))}
        </div>
      </div>

      {loading ? <LoadingSpinner /> : data.items.length === 0 ? (
        <EmptyState title="No trends yet" message='Click "Sync" to load trending AI topics.' icon={TrendingUp} />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {data.items.map((trend, i) => (
            <div key={trend.id} className="card flex gap-4 items-start animate-slide-up">
              <div className="text-2xl font-bold text-slate-700 w-8 shrink-0 mt-0.5">
                {i + 1}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2 mb-1">
                  <h3 className="text-white font-semibold text-sm leading-snug">{trend.topic}</h3>
                  <div className={`flex items-center gap-1 text-xs font-bold shrink-0 ${heatColor(trend.mentions, maxMentions)}`}>
                    <Flame size={12} /> {(trend.mentions / 1000).toFixed(1)}k
                  </div>
                </div>
                {trend.description && (
                  <p className="text-slate-500 text-xs leading-relaxed line-clamp-2">{trend.description}</p>
                )}
                <div className="mt-2 flex items-center gap-2">
                  {trend.category && (
                    <span className={`badge text-[10px] bg-gradient-to-r ${CATEGORY_COLORS[trend.category] || 'from-gray-600 to-gray-800'} text-white`}>
                      {trend.category}
                    </span>
                  )}
                  <div className="flex-1 bg-bg-hover rounded-full h-1.5">
                    <div
                      className="bg-gradient-to-r from-accent-purple to-accent-cyan h-1.5 rounded-full"
                      style={{ width: `${(trend.mentions / maxMentions) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
