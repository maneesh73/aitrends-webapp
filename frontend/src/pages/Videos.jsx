import { useState } from 'react'
import { Youtube, Eye, ThumbsUp, Calendar, ExternalLink } from 'lucide-react'
import { usePaginatedFetch } from '../hooks/useFetch'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import Pagination from '../components/Pagination'
import SearchBar from '../components/SearchBar'

function formatNum(n) {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K'
  return n
}

function VideoCard({ video }) {
  return (
    <div className="card flex flex-col gap-3 animate-slide-up">
      <a href={video.url} target="_blank" rel="noopener noreferrer" className="block relative group">
        {video.thumbnail ? (
          <img src={video.thumbnail} alt={video.title} className="w-full h-40 object-cover rounded-lg bg-bg-hover" />
        ) : (
          <div className="w-full h-40 rounded-lg bg-bg-hover flex items-center justify-center">
            <Youtube size={32} className="text-red-500" />
          </div>
        )}
        <div className="absolute inset-0 bg-black/40 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
          <div className="w-12 h-12 rounded-full bg-red-600 flex items-center justify-center">
            <svg viewBox="0 0 24 24" fill="white" className="w-5 h-5 ml-0.5"><path d="M8 5v14l11-7z"/></svg>
          </div>
        </div>
      </a>
      <div>
        <div className="text-slate-500 text-[10px] mb-1">{video.channel}</div>
        <h3 className="text-white font-semibold text-sm leading-snug line-clamp-2">{video.title}</h3>
      </div>
      {video.summary && (
        <p className="text-slate-500 text-xs leading-relaxed line-clamp-2">{video.summary}</p>
      )}
      <div className="flex items-center gap-3 mt-auto pt-2 border-t border-border text-xs text-slate-500">
        {video.view_count > 0 && (
          <span className="flex items-center gap-1"><Eye size={10} /> {formatNum(video.view_count)}</span>
        )}
        {video.like_count > 0 && (
          <span className="flex items-center gap-1"><ThumbsUp size={10} /> {formatNum(video.like_count)}</span>
        )}
        {video.published_at && (
          <span className="flex items-center gap-1 ml-auto">
            <Calendar size={10} /> {new Date(video.published_at).toLocaleDateString()}
          </span>
        )}
      </div>
    </div>
  )
}

export default function Videos() {
  const [search, setSearch] = useState('')
  const { data, page, setPage, loading } = usePaginatedFetch('/api/trends/videos', { search })

  return (
    <div className="space-y-5 animate-fade-in">
      <div>
        <h1 className="section-title">AI Videos</h1>
        <p className="section-subtitle">YouTube AI tutorials, lectures, demos and talks</p>
        <SearchBar value={search} onChange={setSearch} placeholder="Search videos..." />
      </div>

      {loading ? <LoadingSpinner /> : data.items.length === 0 ? (
        <EmptyState title="No videos yet" message='Add a YouTube API key and click "Sync" to load AI videos.' icon={Youtube} />
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {data.items.map(v => <VideoCard key={v.id} video={v} />)}
          </div>
          <Pagination page={page} hasNext={data.has_next} total={data.total} pageSize={12}
            onPrev={() => setPage(p => p - 1)} onNext={() => setPage(p => p + 1)} />
        </>
      )}
    </div>
  )
}
