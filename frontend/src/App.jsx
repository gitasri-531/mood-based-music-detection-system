import React, { useEffect, useState, useCallback } from 'react'
import { Camera, Music as MusicIcon, BarChart3, Brain, Settings as Cog, LayoutDashboard, LogOut } from 'lucide-react'
import { api, ghost } from './ui'
import { Welcome, AuthForm } from './Auth.jsx'
import Detect from './Detect.jsx'
import Music from './Music.jsx'
import { Dashboard, History, Insights, Settings } from './Pages.jsx'

const NAV = [['dashboard', 'Dashboard', LayoutDashboard], ['detect', 'Detect', Camera], ['music', 'Music', MusicIcon], ['history', 'History', BarChart3], ['insights', 'Model', Brain], ['settings', 'Settings', Cog]]

export default function App() {
  const [user, setUser] = useState(undefined), [view, setView] = useState('welcome'), [result, setResult] = useState(null), [tick, setTick] = useState(0)
  const refresh = useCallback(() => setTick(t => t + 1), [])
  useEffect(() => { api('/api/auth/me').then(j => { setUser(j.user); setView('dashboard') }).catch(() => setUser(null)) }, [])
  useEffect(() => { const f = () => { setUser(null); setResult(null); setView('login') }; window.addEventListener('auth-expired', f); return () => window.removeEventListener('auth-expired', f) }, [])
  const onAuth = u => { setUser(u); setView('dashboard') }
  const logout = async () => { setView('welcome'); setResult(null); setUser(null); await api('/api/auth/logout', { method: 'POST' }).catch(() => {}) } // unmounting Detect stops the camera
  if (user === undefined) return <p className="p-10 text-center text-white/60">Loading…</p>
  if (!user) return view === 'login' || view === 'signup' ? <AuthForm key={view} mode={view} go={setView} onAuth={onAuth} /> : <Welcome go={setView} />
  return (<div className="mx-auto max-w-5xl p-4">
    <nav className="flex flex-wrap items-center justify-between gap-2 py-3" aria-label="Main">
      <span className="text-xl font-bold bg-gradient-to-r from-violet-300 to-fuchsia-300 bg-clip-text text-transparent">MoodTune AI</span>
      <div className="flex flex-wrap gap-1">
        {NAV.map(([k, l, I]) => <button key={k} onClick={() => setView(k)} aria-current={view === k} className={`flex items-center gap-1 rounded-lg px-3 py-1.5 text-sm ${view === k ? 'bg-violet-600' : 'hover:bg-white/10'}`}><I size={15} /><span className="hidden sm:inline">{l}</span></button>)}
        <button className={ghost} onClick={logout}><LogOut size={14} /><span className="hidden sm:inline">Logout</span></button></div>
    </nav>
    {view === 'dashboard' && <Dashboard user={user} go={setView} tick={tick} />}
    {view === 'detect' && <Detect result={result} onResult={setResult} go={setView} />}
    {view === 'music' && <Music result={result} user={user} go={setView} refresh={refresh} />}
    {view === 'history' && <History tick={tick} refresh={refresh} />}
    {view === 'insights' && <Insights />}
    {view === 'settings' && <Settings user={user} onUser={setUser} refresh={refresh} />}
  </div>)
}
