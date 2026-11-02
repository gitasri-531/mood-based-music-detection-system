import React, { useEffect, useState } from 'react'
import { Camera, Trash2 } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, CartesianGrid } from 'recharts'
import { api, card, btn, ghost, input, LANGS } from './ui'

export function History({ tick, refresh }) {
  const [an, setAn] = useState(null), [h, setH] = useState([])
  useEffect(() => { api('/api/analytics').then(setAn).catch(() => {}); api('/api/history').then(j => setH(j.history)).catch(() => {}) }, [tick])
  const clear = async () => { if (confirm('Delete all saved mood history?')) { await api('/api/history?confirm=true', { method: 'DELETE' }); refresh() } }
  if (!an || !an.total) return <div className={card}>No saved history yet. Open Recommendations and click “Save to history”.</div>
  return (<div className="grid gap-5 md:grid-cols-2">
    <div className={card}><h2 className="font-semibold mb-2">Expression distribution</h2><div className="h-56"><ResponsiveContainer><BarChart data={an.distribution}>
      <XAxis dataKey="emotion" stroke="#aaa" fontSize={11} /><YAxis allowDecimals={false} stroke="#aaa" /><Tooltip /><Bar dataKey="n" fill="#8b5cf6" radius={4} /></BarChart></ResponsiveContainer></div></div>
    <div className={card}><h2 className="font-semibold mb-2">Entries per day</h2><div className="h-56"><ResponsiveContainer><LineChart data={an.daily}>
      <CartesianGrid stroke="#333" /><XAxis dataKey="day" stroke="#aaa" fontSize={11} /><YAxis allowDecimals={false} stroke="#aaa" /><Tooltip /><Line dataKey="n" stroke="#a78bfa" /></LineChart></ResponsiveContainer></div></div>
    <div className={card + ' md:col-span-2'}><div className="flex justify-between mb-2"><h2 className="font-semibold">Recent entries (stored locally in SQLite)</h2>
      <button className={btn} onClick={clear}><Trash2 size={14} />Clear</button></div>
      <ul className="text-sm space-y-1">{h.slice(0, 15).map(x => <li key={x.id}>{x.ts} — <b className="capitalize">{x.emotion}</b> ({x.source}) → {x.goal}</li>)}</ul></div></div>)
}

export function Insights() {
  const [s, setS] = useState(null)
  useEffect(() => { api('/api/model/status').then(setS).catch(() => setS({ message: 'Backend not reachable.' })) }, [])
  if (!s) return <div className={card}>Loading…</div>
  const m = s.metrics, hist = s.history
  return (<div className="space-y-4">
    <div className={card}><h2 className="font-semibold">Model</h2><p className="text-sm text-white/70 mt-1">CNN (3 conv blocks, max-pooling, dropout, dense 256, 7-way softmax) trained on FER-2013 (48×48 grayscale). Model loaded from disk: <b>{s.model_available ? 'yes' : 'no'}</b>.</p>
      {s.message && <p className="mt-2 text-amber-300 text-sm">{s.message}</p>}</div>
    {m ? <div className={card}><h2 className="font-semibold">Test results</h2><p>Accuracy {(m.accuracy * 100).toFixed(1)}% · Macro-F1 {m.macro_f1.toFixed(3)}</p>
      <div className="h-56 mt-2"><ResponsiveContainer><BarChart data={m.classes.map(c => ({ c, f1: +m.per_class[c].f1.toFixed(3) }))}><XAxis dataKey="c" stroke="#aaa" fontSize={11} /><YAxis stroke="#aaa" /><Tooltip /><Bar dataKey="f1" fill="#8b5cf6" /></BarChart></ResponsiveContainer></div></div>
      : <div className={card}>Evaluation pending: run <code>python evaluate_model.py</code> after training.</div>}
    {hist && <div className={card}><h2 className="font-semibold">Training curves</h2><div className="h-56"><ResponsiveContainer><LineChart data={hist.accuracy.map((a, i) => ({ epoch: i + 1, train: a, val: hist.val_accuracy[i] }))}>
      <CartesianGrid stroke="#333" /><XAxis dataKey="epoch" stroke="#aaa" /><YAxis stroke="#aaa" /><Tooltip /><Line dataKey="train" stroke="#a78bfa" /><Line dataKey="val" stroke="#f0abfc" /></LineChart></ResponsiveContainer></div></div>}
  </div>)
}

export function Dashboard({ user, go, tick }) {
  const [h, setH] = useState([]), [an, setAn] = useState(null), [ms, setMs] = useState(null)
  useEffect(() => { api('/api/history').then(j => setH(j.history)).catch(() => {}); api('/api/analytics').then(setAn).catch(() => {}); api('/api/model/status').then(setMs).catch(() => {}) }, [tick])
  const lang = LANGS.find(l => l[0] === user.preferred_language)?.[1] || 'All languages'
  return (<div className="space-y-5 rise">
    <div className={card + ' flex flex-wrap items-center justify-between gap-4'}>
      <div><h1 className="text-2xl font-bold">Welcome, {user.name.split(' ')[0]}</h1>
        <p className="text-sm text-white/60">Preferred language: {lang} · CNN: {ms ? (ms.model_available ? 'ready' : 'not trained yet') : '…'}</p></div>
      <button className={btn} onClick={() => go('detect')}><Camera size={16} />Start detection</button></div>
    {ms && !ms.model_available && <div className={card + ' border-amber-400/30 text-sm text-amber-200'}>{ms.message}</div>}
    <div className="grid gap-5 md:grid-cols-2">
      <div className={card}><h2 className="font-semibold mb-2">Recent predictions</h2>
        {h.length ? <ul className="space-y-1 text-sm">{h.slice(0, 5).map(x => <li key={x.id}><b className="capitalize">{x.emotion}</b> <span className="text-white/50">· {x.ts}</span></li>)}</ul> : <p className="text-sm text-white/60">None yet. Real predictions saved from the Music page appear here.</p>}</div>
      <div className={card}><h2 className="font-semibold mb-2">Recently recommended</h2>
        {h.length ? <ul className="space-y-1 text-sm">{h.slice(0, 1).flatMap(x => x.song_titles.slice(0, 5)).map(t => <li key={t}>{t}</li>)}</ul> : <p className="text-sm text-white/60">Nothing saved yet.</p>}</div>
      {an?.total > 0 && <div className={card + ' md:col-span-2'}><h2 className="font-semibold mb-2">Your expression history</h2><div className="h-44"><ResponsiveContainer><BarChart data={an.distribution}>
        <XAxis dataKey="emotion" stroke="#aaa" fontSize={11} /><YAxis allowDecimals={false} stroke="#aaa" /><Tooltip /><Bar dataKey="n" fill="#a78bfa" radius={4} /></BarChart></ResponsiveContainer></div></div>}
    </div></div>)
}

export function Settings({ user, onUser, refresh }) {
  const [name, setName] = useState(user.name), [lang, setLang] = useState(user.preferred_language || 'All'), [msg, setMsg] = useState('')
  const save = async () => { try { const j = await api('/api/auth/me', { method: 'PATCH', body: JSON.stringify({ name, preferred_language: lang }) }); onUser(j.user); setMsg('Saved.') } catch (e) { setMsg(e.message) } }
  const clear = async () => { if (confirm('Delete all your saved history?')) { await api('/api/history?confirm=true', { method: 'DELETE' }); refresh(); setMsg('History cleared.') } }
  return (<div className="grid gap-5 md:grid-cols-2 rise">
    <div className={card + ' space-y-3'}><h2 className="font-semibold">Profile</h2><p className="text-sm text-white/60">{user.email}</p>
      <label className="text-sm" htmlFor="sn">Name</label><input id="sn" className={input} value={name} onChange={e => setName(e.target.value)} />
      <label className="text-sm" htmlFor="sl">Preferred music language</label>
      <select id="sl" className={input} value={lang} onChange={e => setLang(e.target.value)}>{LANGS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}</select>
      <button className={btn} onClick={save}>Save changes</button>{msg && <p role="status" className="text-sm text-violet-200">{msg}</p>}</div>
    <div className={card + ' space-y-3'}><h2 className="font-semibold">Privacy</h2>
      <p className="text-sm text-white/70">Webcam frames are processed in memory and discarded. Only the predicted expression, confidence, goal and song ids are stored, in a local SQLite file, tied to your account. Facial-expression predictions are imperfect and are not psychological diagnoses.</p>
      <button className={ghost} onClick={clear}><Trash2 size={14} />Clear my history</button></div></div>)
}
