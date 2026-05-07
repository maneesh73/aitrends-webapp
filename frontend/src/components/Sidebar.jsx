import { NavLink } from 'react-router-dom'
import {
  Newspaper, FlaskConical, GraduationCap, Github,
  Bot, TrendingUp, Home, Youtube, Zap
} from 'lucide-react'
import clsx from 'clsx'

const NAV_ITEMS = [
  { to: '/', icon: Home, label: 'Home', exact: true },
  { to: '/news', icon: Newspaper, label: 'AI News' },
  { to: '/research', icon: FlaskConical, label: 'Research & Papers' },
  { to: '/courses', icon: GraduationCap, label: 'Courses' },
  { to: '/github', icon: Github, label: 'GitHub Repos' },
  { to: '/agents', icon: Bot, label: 'Agents & Tools' },
  { to: '/trends', icon: TrendingUp, label: 'Trends' },
  { to: '/videos', icon: Youtube, label: 'Videos' },
]

export default function Sidebar() {
  return (
    <aside className="w-60 shrink-0 bg-bg-secondary border-r border-border flex flex-col h-full">
      <div className="p-5 border-b border-border">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-purple to-accent-cyan flex items-center justify-center shrink-0">
            <Zap size={16} className="text-white" />
          </div>
          <div>
            <div className="text-white font-bold text-base leading-tight">AI Pulse</div>
            <div className="text-slate-500 text-[10px] leading-tight">AI Hub & Trends</div>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-3 space-y-0.5 overflow-y-auto">
        <div className="text-[10px] font-semibold text-slate-600 uppercase tracking-widest px-3 py-2">Navigation</div>
        {NAV_ITEMS.map(({ to, icon: Icon, label, exact }) => (
          <NavLink
            key={to}
            to={to}
            end={exact}
            className={({ isActive }) =>
              clsx('nav-link', { active: isActive })
            }
          >
            <Icon size={16} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-border">
        <div className="text-xs text-slate-600 text-center">
          Powered by arXiv · GitHub · HuggingFace · NewsAPI
        </div>
      </div>
    </aside>
  )
}
