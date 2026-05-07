import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Topbar from './components/Topbar'
import Home from './pages/Home'
import News from './pages/News'
import Research from './pages/Research'
import Courses from './pages/Courses'
import GitHub from './pages/GitHub'
import Agents from './pages/Agents'
import Trends from './pages/Trends'
import Videos from './pages/Videos'

export default function App() {
  return (
    <div className="flex h-screen overflow-hidden bg-bg-primary">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Topbar />
        <main className="flex-1 overflow-y-auto p-6">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/news" element={<News />} />
            <Route path="/research" element={<Research />} />
            <Route path="/courses" element={<Courses />} />
            <Route path="/github" element={<GitHub />} />
            <Route path="/agents" element={<Agents />} />
            <Route path="/trends" element={<Trends />} />
            <Route path="/videos" element={<Videos />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}
