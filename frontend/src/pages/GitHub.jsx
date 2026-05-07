import { useState } from 'react'
import { Star, GitFork, ExternalLink, Github } from 'lucide-react'
import { usePaginatedFetch } from '../hooks/useFetch'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import Pagination from '../components/Pagination'
import SearchBar from '../components/SearchBar'

const LANGUAGES = ['', 'Python', 'JavaScript', 'TypeScript', 'Rust', 'Go', 'C++', 'Java']

function formatStars(n) {
  if (n >= 1000) return (n / 1000).toFixed(1) + 'k'
  return n
}

function RepoCard({ repo }) {
  return (
    <div className="card flex flex-col gap-3 animate-slide-up">
      <div className="flex items-center gap-3">
        {repo.owner_avatar ? (
          <img src={repo.owner_avatar} alt="" className="w-8 h-8 rounded-full bg-bg-hover" />
        ) : (
          <div className="w-8 h-8 rounded-full bg-bg-hover flex items-center justify-center">
            <Github size={16} className="text-slate-500" />
          </div>
        )}
        <div className="min-w-0">
          <div className="text-white font-semibold text-sm truncate">{repo.name}</div>
          <div className="text-slate-600 text-[10px] truncate">{repo.full_name}</div>
        </div>
      </div>
      {repo.description && (
        <p className="text-slate-400 text-xs leading-relaxed line-clamp-3">{repo.description}</p>
      )}
      <div className="flex flex-wrap gap-1">
        {(repo.topics || []).slice(0, 5).map(t => (
          <span key={t} className="badge bg-bg-hover text-slate-500 text-[10px]">{t}</span>
        ))}
      </div>
      <div className="flex items-center gap-4 mt-auto pt-2 border-t border-border">
        {repo.language && (
          <span className="text-xs text-slate-400 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-yellow-400 inline-block" /> {repo.language}
          </span>
        )}
        <span className="text-xs text-slate-400 flex items-center gap-1 ml-auto">
          <Star size={11} className="text-yellow-400" /> {formatStars(repo.stars)}
        </span>
        <span className="text-xs text-slate-400 flex items-center gap-1">
          <GitFork size={11} /> {formatStars(repo.forks)}
        </span>
        <a href={repo.url} target="_blank" rel="noopener noreferrer"
          className="text-slate-500 hover:text-white transition-colors">
          <ExternalLink size={13} />
        </a>
      </div>
    </div>
  )
}

export default function GitHub() {
  const [search, setSearch] = useState('')
  const [language, setLanguage] = useState('')
  const { data, page, setPage, loading } = usePaginatedFetch('/api/github/repos', { search, language })

  return (
    <div className="space-y-5 animate-fade-in">
      <div>
        <h1 className="section-title">GitHub Repositories</h1>
        <p className="section-subtitle">Trending and top AI/ML repositories on GitHub</p>
        <div className="flex flex-col sm:flex-row gap-3">
          <SearchBar value={search} onChange={setSearch} placeholder="Search repositories..." />
          <div className="flex gap-1 flex-wrap">
            {LANGUAGES.map(l => (
              <button key={l} onClick={() => setLanguage(l)}
                className={`px-3 py-1.5 text-xs rounded-lg border transition-colors ${
                  language === l ? 'bg-accent-purple text-white border-accent-purple' : 'bg-bg-card text-slate-400 border-border hover:border-border-light'
                }`}>{l || 'All'}</button>
            ))}
          </div>
        </div>
      </div>

      {loading ? <LoadingSpinner /> : data.items.length === 0 ? (
        <EmptyState title="No repositories yet" message='Click "Sync" to fetch trending AI GitHub repos.' icon={Github} />
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {data.items.map(r => <RepoCard key={r.id} repo={r} />)}
          </div>
          <Pagination page={page} hasNext={data.has_next} total={data.total} pageSize={12}
            onPrev={() => setPage(p => p - 1)} onNext={() => setPage(p => p + 1)} />
        </>
      )}
    </div>
  )
}
