import { useState } from 'react'
import { ExternalLink, FileText, Calendar, Users } from 'lucide-react'
import { usePaginatedFetch } from '../hooks/useFetch'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import Pagination from '../components/Pagination'
import SearchBar from '../components/SearchBar'

const ARXIV_CATS = [
  { value: '', label: 'All' },
  { value: 'cs.AI', label: 'AI' },
  { value: 'cs.LG', label: 'Machine Learning' },
  { value: 'cs.CL', label: 'Computation & Language' },
  { value: 'cs.CV', label: 'Computer Vision' },
  { value: 'stat.ML', label: 'Statistics ML' },
]

function PaperCard({ paper }) {
  return (
    <div className="card flex flex-col gap-3 animate-slide-up">
      <div className="flex flex-wrap gap-1.5">
        {(paper.categories || []).slice(0, 3).map(cat => (
          <span key={cat} className="badge bg-purple-500/10 text-purple-400 border border-purple-500/20 text-[10px]">
            {cat}
          </span>
        ))}
      </div>
      <h3 className="text-white font-semibold text-sm leading-snug line-clamp-3">{paper.title}</h3>
      {paper.abstract && (
        <p className="text-slate-500 text-xs leading-relaxed line-clamp-4">{paper.abstract}</p>
      )}
      {paper.authors?.length > 0 && (
        <div className="text-slate-600 text-xs flex items-center gap-1">
          <Users size={10} /> {paper.authors.slice(0, 3).join(', ')}{paper.authors.length > 3 ? ' et al.' : ''}
        </div>
      )}
      {paper.published_at && (
        <div className="text-slate-600 text-xs flex items-center gap-1">
          <Calendar size={10} /> {new Date(paper.published_at).toLocaleDateString()}
        </div>
      )}
      <div className="flex gap-2 mt-auto">
        <a href={paper.url} target="_blank" rel="noopener noreferrer"
          className="flex items-center gap-1 text-accent-cyan text-xs font-medium hover:underline">
          <FileText size={11} /> Abstract
        </a>
        {paper.pdf_url && (
          <a href={paper.pdf_url} target="_blank" rel="noopener noreferrer"
            className="flex items-center gap-1 text-red-400 text-xs font-medium hover:underline">
            <ExternalLink size={11} /> PDF
          </a>
        )}
      </div>
    </div>
  )
}

export default function Research() {
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('')
  const { data, page, setPage, loading } = usePaginatedFetch('/api/research/papers', { search, category })

  return (
    <div className="space-y-5 animate-fade-in">
      <div>
        <h1 className="section-title">Research & Papers</h1>
        <p className="section-subtitle">Latest AI research from arXiv — papers, white papers, and publications</p>
        <div className="flex flex-col sm:flex-row gap-3">
          <SearchBar value={search} onChange={setSearch} placeholder="Search papers..." />
          <div className="flex gap-1 flex-wrap">
            {ARXIV_CATS.map(c => (
              <button
                key={c.value}
                onClick={() => setCategory(c.value)}
                className={`px-3 py-1.5 text-xs rounded-lg border transition-colors ${
                  category === c.value
                    ? 'bg-accent-purple text-white border-accent-purple'
                    : 'bg-bg-card text-slate-400 border-border hover:border-border-light'
                }`}
              >
                {c.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {loading ? (
        <LoadingSpinner />
      ) : data.items.length === 0 ? (
        <EmptyState title="No papers yet" message='Click "Sync" to fetch latest arXiv research papers.' />
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {data.items.map(p => <PaperCard key={p.id} paper={p} />)}
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
