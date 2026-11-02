import React, { useState } from 'react'
import { Eye, EyeOff, Loader2, ScanFace, Music, ShieldCheck, Check } from 'lucide-react'
import { api, btn, ghost, input, card } from './ui'

export function Welcome({ go }) {
  return (
    <div className="relative overflow-hidden">
      <div className="pointer-events-none absolute -top-24 -left-24 h-72 w-72 rounded-full bg-violet-600/30 blur-3xl animate-pulse" />
      <div className="pointer-events-none absolute top-40 -right-24 h-72 w-72 rounded-full bg-fuchsia-600/20 blur-3xl animate-pulse" />
      <header className="mx-auto flex max-w-5xl items-center justify-between p-5">
        <span className="text-xl font-bold bg-gradient-to-r from-violet-300 to-fuchsia-300 bg-clip-text text-transparent">MoodTune AI</span>
        <div className="flex gap-2"><button className={ghost} onClick={() => go('login')}>Login</button><button className={btn} onClick={() => go('signup')}>Create account</button></div>
      </header>
      <main className="relative mx-auto max-w-3xl px-5 py-16 text-center rise">
        <h1 className="text-4xl sm:text-6xl font-extrabold leading-tight bg-gradient-to-r from-violet-200 via-violet-400 to-fuchsia-400 bg-clip-text text-transparent">Music that follows your expression</h1>
        <p className="mx-auto mt-5 max-w-xl text-white/70">A CNN trained on FER-2013 reads your webcam in real time and suggests Telugu, Hindi and English songs through transparent, editable rules.</p>
        <div className="mt-8 flex justify-center gap-3"><button className={btn} onClick={() => go('signup')}>Get started</button><button className={ghost} onClick={() => go('login')}>I have an account</button></div>
        <div className="mt-14 grid gap-4 sm:grid-cols-3 text-left">
          {[[ScanFace, 'Live detection', 'Webcam frames are analysed by a CNN; nothing is saved.'], [Music, 'Telugu · Hindi · English', 'Pick your language and listening goal.'], [ShieldCheck, 'Private by design', 'Only prediction metadata is stored, per account.']].map(([I, t, d]) =>
            <div key={t} className={card}><I className="text-fuchsia-300" size={22} /><h3 className="mt-2 font-semibold">{t}</h3><p className="text-sm text-white/60">{d}</p></div>)}
        </div>
        <p className="mt-8 text-xs text-white/40">Predictions are imperfect guesses about facial expression, not diagnoses of how you feel.</p>
      </main>
    </div>)
}

const checks = pw => [['8+ characters', pw.length >= 8], ['A letter', /[A-Za-z]/.test(pw)], ['A number', /\d/.test(pw)]]

export function AuthForm({ mode, go, onAuth }) {
  const signup = mode === 'signup'
  const [f, setF] = useState({ name: '', email: '', password: '', confirm: '' }), [show, setShow] = useState(false)
  const [err, setErr] = useState(''), [busy, setBusy] = useState(false), [ok, setOk] = useState(false)
  const set = k => e => setF({ ...f, [k]: e.target.value })
  const submit = async e => {
    e.preventDefault(); setErr('')
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(f.email)) return setErr('Enter a valid email address.')
    if (signup) {
      if (f.name.trim().length < 2) return setErr('Please enter your full name.')
      if (!checks(f.password).every(c => c[1])) return setErr('Password does not meet the requirements.')
      if (f.password !== f.confirm) return setErr('Passwords do not match.')
    } else if (!f.password) return setErr('Enter your password.')
    setBusy(true)
    try {
      const j = await api(signup ? '/api/auth/register' : '/api/auth/login', { method: 'POST', body: JSON.stringify({ name: f.name, email: f.email, password: f.password }) })
      setOk(true); setTimeout(() => onAuth(j.user), 500)
    } catch (e) { setErr(e.message); setBusy(false) }
  }
  return (
    <div className="mx-auto flex min-h-screen max-w-md flex-col justify-center p-5 rise">
      <button onClick={() => go('welcome')} className="mb-6 text-left text-lg font-bold text-violet-300">MoodTune AI</button>
      <form onSubmit={submit} className={card} noValidate aria-label={signup ? 'Create account' : 'Login'}>
        <h1 className="text-2xl font-bold">{signup ? 'Create your account' : 'Welcome back'}</h1>
        <div className="mt-5 space-y-3">
          {signup && <div><label className="text-sm text-white/70" htmlFor="n">Full name</label><input id="n" className={input} value={f.name} onChange={set('name')} autoComplete="name" /></div>}
          <div><label className="text-sm text-white/70" htmlFor="e">Email</label><input id="e" type="email" className={input} value={f.email} onChange={set('email')} autoComplete="email" /></div>
          <div><label className="text-sm text-white/70" htmlFor="p">Password</label>
            <div className="relative"><input id="p" type={show ? 'text' : 'password'} className={input} value={f.password} onChange={set('password')} autoComplete={signup ? 'new-password' : 'current-password'} />
              <button type="button" aria-label={show ? 'Hide password' : 'Show password'} onClick={() => setShow(!show)} className="absolute right-3 top-2.5 text-white/60">{show ? <EyeOff size={18} /> : <Eye size={18} />}</button></div></div>
          {signup && <>
            <div><label className="text-sm text-white/70" htmlFor="c">Confirm password</label><input id="c" type={show ? 'text' : 'password'} className={input} value={f.confirm} onChange={set('confirm')} autoComplete="new-password" /></div>
            <ul className="flex flex-wrap gap-3 text-xs">{checks(f.password).map(([t, v]) => <li key={t} className={v ? 'text-emerald-300' : 'text-white/40'}><Check size={12} className="inline" /> {t}</li>)}</ul></>}
        </div>
        {err && <p role="alert" className="mt-3 text-sm text-red-300">{err}</p>}
        <button className={btn + ' mt-5 w-full'} disabled={busy}>{ok ? 'Success!' : busy ? <><Loader2 className="animate-spin" size={16} />Please wait…</> : signup ? 'Create account' : 'Login'}</button>
        <p className="mt-4 text-center text-sm text-white/60">{signup ? 'Already registered?' : 'New here?'} <button type="button" className="text-fuchsia-300 underline" onClick={() => go(signup ? 'login' : 'signup')}>{signup ? 'Login' : 'Create an account'}</button></p>
      </form>
    </div>)
}
