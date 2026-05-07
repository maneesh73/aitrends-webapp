import { useState } from 'react'
import { ExternalLink, Clock, User, Tag } from 'lucide-react'
import { usePaginatedFetch } from '../hooks/useFetch'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import Pagination from '../components/Pagination'
import SearchBar from '../components/SearchBar'

function timeAgo(dateStr) {
  if (!dateStr) return ''
  const diff = Date.now() - new Date(dateStr).getTime()
  const h = Math.floor(diff / 3600000)
  if (h < 1) return 'just now'
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}

function ArticleCard({ article }) {
  return (
    <div className="card flex flex-col gap-3 animate-slide-up">
      {article.image_url && (
        <img
          src={article.image_url}
          alt={article.title}
          className="w-full h-36 object-cover rounded-lg bg-bg-hover"
          onError={e => { e.target.style.display = 'none' }}
        />
      )}
      <div className="flex items-center gap-2">
        {article.source && (
          <span className="badge bg-blue-500/10 text-blue-400 border border-blue-500/20">
            {article.source}
          </span>
        )}
        <span className="text-slate-600 text-xs flex items-center gap-1">
          <Clock size={10} /> {timeAgo(article.published_at)}
        </span>
      </div>
      <h3 className="text-white font-semibold text-sm leading-snug line-clamp-2">
        {article.title}
      </h3>
      {article.description && (
        <p className="text-slate-500 text-xs leading-relaxed line-clamp-3">{article.description}</p>
      )}
      {article.author && (
        <div className="text-slate-600 text-xs flex items-center gap-1">
          <User size={10} /> {article.author}
        </div>
      )}
      <a
        href={article.url}
        target="_blank"
        rel="noopener noreferrer"
        className="mt-auto flex items-center gap-1 text-accent-cyan text-xs font-medium hover:underline"
      >
        Read article <ExternalLink size={11} />
      </a>
    </div>
  )
}

export default function News() {
  const [search, setSearch] = useState('')
  const { data, page, setPage, loading } = usePaginatedFetch('/api/news', { search })

  return (
    <div className="space-y-5 animate-fade-in">
      <div>
        <h1 className="section-title">AI News</h1>
        <p className="section-subtitle">Latest AI headlines from MIT Tech Review, VentureBeat, The Verge and more</p>
        <SearchBar value={search} onChange={setSearch} placeholder="Search articles..." />
      </div>

      {loading ? (
        <LoadingSpinner />
      ) : data.items.length === 0 ? (
        <EmptyState title="No articles yet" message='Click "Sync" in the top bar to fetch the latest AI news.' />
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {data.items.map(a => <ArticleCard key={a.id} article={a} />)}
          </div>
          <Pagination
            page={page} hasNext={data.has_next} total={data.total} pageSize={12}
            onPrev={() => setPage(p => p - 1)} onNext={() => setPage(p => p + 1)}
          />
        </>
      )}
    </div>
  )
}
