import { useState } from 'react'
import { ExternalLink, GraduationCap, Clock, CheckCircle, DollarSign } from 'lucide-react'
import { usePaginatedFetch } from '../hooks/useFetch'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import Pagination from '../components/Pagination'
import SearchBar from '../components/SearchBar'

const LEVELS = ['', 'Beginner', 'Intermediate', 'Advanced']

function CourseCard({ course }) {
  return (
    <div className="card flex flex-col gap-3 animate-slide-up">
      {course.thumbnail ? (
        <img src={course.thumbnail} alt={course.title} className="w-full h-32 object-cover rounded-lg bg-bg-hover"
          onError={e => { e.target.style.display = 'none' }} />
      ) : (
        <div className="w-full h-32 rounded-lg bg-gradient-to-br from-green-900/40 to-bg-hover flex items-center justify-center">
          <GraduationCap size={32} className="text-green-600" />
        </div>
      )}
      <div className="flex flex-wrap gap-1.5">
        {course.level && (
          <span className={`badge ${
            course.level === 'Beginner' ? 'bg-green-500/10 text-green-400 border-green-500/20' :
            course.level === 'Advanced' ? 'bg-red-500/10 text-red-400 border-red-500/20' :
            'bg-yellow-500/10 text-yellow-400 border-yellow-500/20'
          } border text-[10px]`}>{course.level}</span>
        )}
        <span className={`badge border text-[10px] ${
          course.is_free ? 'bg-green-500/10 text-green-400 border-green-500/20' : 'bg-slate-500/10 text-slate-400 border-slate-500/20'
        }`}>
          {course.is_free ? '✓ Free' : 'Paid'}
        </span>
      </div>
      <h3 className="text-white font-semibold text-sm leading-snug line-clamp-2">{course.title}</h3>
      {course.description && (
        <p className="text-slate-500 text-xs leading-relaxed line-clamp-3">{course.description}</p>
      )}
      <div className="text-slate-600 text-xs space-y-1">
        {course.provider && <div>📚 {course.provider}</div>}
        {course.instructor && <div>👤 {course.instructor}</div>}
        {course.duration && <div className="flex items-center gap-1"><Clock size={10} /> {course.duration}</div>}
      </div>
      {course.topics?.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {course.topics.slice(0, 4).map(t => (
            <span key={t} className="badge bg-bg-hover text-slate-500 text-[10px]">{t}</span>
          ))}
        </div>
      )}
      <a href={course.url} target="_blank" rel="noopener noreferrer"
        className="mt-auto flex items-center gap-1 text-accent-cyan text-xs font-medium hover:underline">
        View course <ExternalLink size={11} />
      </a>
    </div>
  )
}

export default function Courses() {
  const [search, setSearch] = useState('')
  const [level, setLevel] = useState('')
  const [isFree, setIsFree] = useState(null)
  const { data, page, setPage, loading } = usePaginatedFetch('/api/courses', {
    search, level, ...(isFree !== null ? { is_free: isFree } : {})
  })

  return (
    <div className="space-y-5 animate-fade-in">
      <div>
        <h1 className="section-title">AI Courses</h1>
        <p className="section-subtitle">Curated AI/ML learning resources from Coursera, fast.ai, Harvard, and more</p>
        <div className="flex flex-col sm:flex-row gap-3">
          <SearchBar value={search} onChange={setSearch} placeholder="Search courses..." />
          <div className="flex gap-1 flex-wrap">
            {LEVELS.map(l => (
              <button key={l} onClick={() => setLevel(l)}
                className={`px-3 py-1.5 text-xs rounded-lg border transition-colors ${
                  level === l ? 'bg-accent-purple text-white border-accent-purple' : 'bg-bg-card text-slate-400 border-border hover:border-border-light'
                }`}>{l || 'All Levels'}</button>
            ))}
            <button onClick={() => setIsFree(isFree === true ? null : true)}
              className={`px-3 py-1.5 text-xs rounded-lg border transition-colors ${
                isFree === true ? 'bg-green-600 text-white border-green-600' : 'bg-bg-card text-slate-400 border-border hover:border-border-light'
              }`}>Free Only</button>
          </div>
        </div>
      </div>

      {loading ? <LoadingSpinner /> : data.items.length === 0 ? (
        <EmptyState title="No courses yet" message='Click "Sync" to load curated AI courses.' icon={GraduationCap} />
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {data.items.map(c => <CourseCard key={c.id} course={c} />)}
          </div>
          <Pagination page={page} hasNext={data.has_next} total={data.total} pageSize={12}
            onPrev={() => setPage(p => p - 1)} onNext={() => setPage(p => p + 1)} />
        </>
      )}
    </div>
  )
}
