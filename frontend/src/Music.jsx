import React, { useEffect, useState, useCallback } from 'react'
import { ExternalLink, Save } from 'lucide-react'
import { api, card, btn, ghost, LANGS } from './ui'

const GOALS = ['auto', 'match', 'relax', 'energize', 'uplift', 'comfort']
export default function Music({ result, user, go, refresh }) {
  const [lang, setLang] = useState(user.preferred_language || 'All'), [goal, setGoal] = useState('auto'), [genre, setGenre] = useState(''), [energy, setEnergy] = useState('')
  const [genres, setGenres] = useState([]), [data, setData] = useState(null), [err, setErr] = useState(''), [saved, setSaved] = useState(false)
  useEffect(() => { api('/api/catalogue/options').then(j => setGenres(j.genres)).catch(() => {}) }, [])
  const load = useCallback(async (save = false) => {
    try {
      const j = result
        ? await api('/api/recommendations', { method: 'POST', body: JSON.stringify({ token: result.token, goal, genre, energy, language: lang, save }) })
        : await api(`/api/catalogue?language=${lang}&genre=${encodeURIComponent(genre)}&energy=${energy}`)
      setData(j); setErr(''); if (save) { setSaved(true); refresh() }
    } catch (e) { setErr(e.message); setData(null) }
  }, [result, goal, genre, energy, lang, refresh])
  useEffect(() => { setSaved(false); load(false) }, [load])
  const sel = 'rounded-lg bg-black/40 border border-white/10 p-1.5 text-sm'
  return (
    <div className="space-y-4 rise">
      <div className={card}>
        <h2 className="text-lg font-semibold">{result ? <>Songs for <span className="capitalize text-violet-300">{result.emotion}</span> · goal: {data?.goal || goal}</> : 'Song catalogue'}</h2>
        {!result && <p className="text-sm text-amber-200/80">Personalised picks need a genuine webcam detection. <button className="underline" onClick={() => go('detect')}>Start detection</button></p>}
        <div className="mt-3 flex flex-wrap gap-2" role="group" aria-label="Language">
          {LANGS.map(([v, l]) => <button key={v} onClick={() => setLang(v)} aria-pressed={lang === v} className={`rounded-full px-3 py-1 text-sm border ${lang === v ? 'bg-violet-600 border-violet-400' : 'border-white/15 hover:bg-white/10'}`}>{l}</button>)}
        </div>
        <div className="mt-3 flex flex-wrap gap-2">
          {result && <select aria-label="Listening goal" className={sel} value={goal} onChange={e => setGoal(e.target.value)}>{GOALS.map(g => <option key={g}>{g}</option>)}</select>}
          <select aria-label="Genre" className={sel} value={genre} onChange={e => setGenre(e.target.value)}><option value="">any genre</option>{genres.map(g => <option key={g}>{g}</option>)}</select>
          <select aria-label="Energy" className={sel} value={energy} onChange={e => setEnergy(e.target.value)}><option value="">any energy</option>{['low', 'medium', 'high'].map(g => <option key={g}>{g}</option>)}</select>
          {result && <button className={btn} onClick={() => load(true)} disabled={saved}><Save size={14} />{saved ? 'Saved' : 'Save to history'}</button>}
          {result && <button className={ghost} onClick={() => load(false)}>Refresh</button>}
        </div>
      </div>
      {err && <p role="alert" className="text-red-300">{err}</p>}
      {data && !data.songs.length && <div className={card}>No songs match these filters. Try another language, genre or energy level.</div>}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {data?.songs.map(s => <div key={s.id} className={card}>
          <div className="flex items-start justify-between gap-2"><h3 className="font-semibold">{s.title}</h3><span className="shrink-0 rounded-full bg-fuchsia-500/20 px-2 py-0.5 text-xs text-fuchsia-200">{s.language}</span></div>
          <p className="text-sm text-white/70">{s.artist}</p><p className="text-xs text-white/50">{s.genre} · {s.energy} energy</p>
          {s.reason && <p className="mt-2 text-xs text-violet-200">{s.reason}</p>}
          <a className={btn + ' mt-3'} href={s.link} target="_blank" rel="noreferrer"><ExternalLink size={14} />Listen ({s.source})</a></div>)}
      </div>
    </div>)
}
