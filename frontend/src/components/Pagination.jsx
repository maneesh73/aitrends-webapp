import { ChevronLeft, ChevronRight } from 'lucide-react'

export default function Pagination({ page, hasNext, onPrev, onNext, total, pageSize }) {
  const start = (page - 1) * pageSize + 1
  const end = Math.min(page * pageSize, total)
  return (
    <div className="flex items-center justify-between pt-4 mt-4 border-t border-border">
      <span className="text-sm text-slate-500">
        Showing {start}–{end} of {total}
      </span>
      <div className="flex gap-2">
        <button
          onClick={onPrev}
          disabled={page === 1}
          className="flex items-center gap-1 px-3 py-1.5 text-sm text-slate-400 hover:text-white bg-bg-hover border border-border rounded-lg disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronLeft size={14} /> Prev
        </button>
        <button
          onClick={onNext}
          disabled={!hasNext}
          className="flex items-center gap-1 px-3 py-1.5 text-sm text-slate-400 hover:text-white bg-bg-hover border border-border rounded-lg disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
        >
          Next <ChevronRight size={14} />
        </button>
      </div>
    </div>
  )
}
