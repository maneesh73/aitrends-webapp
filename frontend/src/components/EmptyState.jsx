import { Database } from 'lucide-react'

export default function EmptyState({ title = 'No data yet', message = 'Click "Sync" to fetch fresh content.', icon: Icon = Database }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-3 text-center">
      <div className="w-12 h-12 rounded-full bg-bg-hover flex items-center justify-center">
        <Icon size={24} className="text-slate-500" />
      </div>
      <h3 className="text-white font-medium">{title}</h3>
      <p className="text-slate-500 text-sm max-w-xs">{message}</p>
    </div>
  )
}
