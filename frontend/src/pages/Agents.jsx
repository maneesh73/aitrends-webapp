import { useState } from 'react'
import { ExternalLink, Github, Star, Bot, Wrench } from 'lucide-react'
import { usePaginatedFetch } from '../hooks/useFetch'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import Pagination from '../components/Pagination'
import SearchBar from '../components/SearchBar'

const CATEGORIES = ['', 'Framework', 'Multi-Agent', 'Agent', 'Platform', 'Runtime', 'SDK', 'App', 'HuggingFace Model']

function ToolCard({ tool }) {
  return (
    <div className="card flex flex-col gap-3 animate-slide-up">
      <div className="flex items-start gap-3">
        {tool.logo_url ? (
          <img src={tool.logo_url} alt="" className="w-9 h-9 rounded-lg bg-bg-hover object-contain p-1 border border-border" />
        ) : (
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-orange-900/40 to-bg-hover border border-border flex items-center justify-center">
            {tool.is_agent ? <Bot size={18} className="text-orange-400" /> : <Wrench size={18} className="text-orange-400" />}
          </div>
        )}
        <div className="min-w-0">
          <div className="text-white font-semibold text-sm">{tool.name}</div>
          <div className="flex gap-1 mt-1 flex-wrap">
            {tool.category && (
              <span className="badge bg-orange-500/10 text-orange-400 border border-orange-500/20 text-[10px]">
                {tool.category}
              </span>
            )}
            {tool.is_agent && (
              <span className="badge bg-purple-500/10 text-purple-400 border border-purple-500/20 text-[10px]">
                <Bot size={9} /> Agent
              </span>
            )}
          </div>
        </div>
      </div>
      {tool.description && (
        <p className="text-slate-400 text-xs leading-relaxed line-clamp-3">{tool.description}</p>
      )}
      {tool.tags?.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {tool.tags.slice(0, 5).map(t => (
            <span key={t} className="badge bg-bg-hover text-slate-500 text-[10px]">{t}</span>
          ))}
        </div>
      )}
      <div className="flex items-center gap-3 mt-auto pt-2 border-t border-border">
        {tool.stars > 0 && (
          <span className="text-xs text-slate-400 flex items-center gap-1">
            <Star size={11} className="text-yellow-400" />
            {tool.stars >= 1000 ? (tool.stars / 1000).toFixed(1) + 'k' : tool.stars}
          </span>
        )}
        <div className="flex gap-2 ml-auto">
          {tool.github_url && (
            <a href={tool.github_url} target="_blank" rel="noopener noreferrer"
              className="text-slate-500 hover:text-white transition-colors">
              <Github size={14} />
            </a>
          )}
          {tool.url && (
            <a href={tool.url} target="_blank" rel="noopener noreferrer"
              className="text-slate-500 hover:text-white transition-colors">
              <ExternalLink size={14} />
            </a>
          )}
        </div>
      </div>
    </div>
  )
}

export default function Agents() {
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('')
  const [agentOnly, setAgentOnly] = useState(null)
  const { data, page, setPage, loading } = usePaginatedFetch('/api/agents', {
    search, category, ...(agentOnly !== null ? { is_agent: agentOnly } : {})
  })

  return (
    <div className="space-y-5 animate-fade-in">
      <div>
        <h1 className="section-title">AI Agents & Tools</h1>
        <p className="section-subtitle">Frameworks, autonomous agents, platforms, and HuggingFace models</p>
        <div className="flex flex-col sm:flex-row gap-3">
          <SearchBar value={search} onChange={setSearch} placeholder="Search tools..." />
          <div className="flex gap-1 flex-wrap">
            <button onClick={() => setAgentOnly(agentOnly === true ? null : true)}
              className={`px-3 py-1.5 text-xs rounded-lg border transition-colors flex items-center gap-1 ${
                agentOnly === true ? 'bg-purple-600 text-white border-purple-600' : 'bg-bg-card text-slate-400 border-border hover:border-border-light'
              }`}><Bot size={11} /> Agents Only</button>
          </div>
        </div>
        <div className="flex gap-1 flex-wrap mt-2">
          {CATEGORIES.map(c => (
            <button key={c} onClick={() => setCategory(c)}
              className={`px-3 py-1.5 text-xs rounded-lg border transition-colors ${
                category === c ? 'bg-accent-purple text-white border-accent-purple' : 'bg-bg-card text-slate-400 border-border hover:border-border-light'
              }`}>{c || 'All'}</button>
          ))}
        </div>
      </div>

      {loading ? <LoadingSpinner /> : data.items.length === 0 ? (
        <EmptyState title="No tools yet" message='Click "Sync" to load AI agents and tools.' icon={Bot} />
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {data.items.map(t => <ToolCard key={t.id} tool={t} />)}
          </div>
          <Pagination page={page} hasNext={data.has_next} total={data.total} pageSize={12}
            onPrev={() => setPage(p => p - 1)} onNext={() => setPage(p => p + 1)} />
        </>
      )}
    </div>
  )
}
