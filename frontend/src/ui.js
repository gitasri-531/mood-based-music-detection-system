export const API = import.meta.env.VITE_API_URL || 'http://localhost:5000'
export const EMOTIONS = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']
export const LANGS = [['All', 'All languages'], ['Telugu', 'తెలుగు'], ['Hindi', 'हिन्दी'], ['English', 'English']]
export const card = 'rounded-2xl border border-white/10 bg-white/[0.04] backdrop-blur p-5 shadow-lg shadow-black/20'
export const btn = 'inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 px-4 py-2 text-sm font-medium focus:outline-none focus-visible:ring-2 focus-visible:ring-fuchsia-300 disabled:opacity-40 transition'
export const ghost = 'inline-flex items-center gap-2 rounded-xl border border-white/15 hover:bg-white/10 px-3 py-2 text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-300 transition'
export const input = 'w-full rounded-xl bg-black/40 border border-white/10 px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400'

export async function api(path, opts = {}) {
  let r
  try {
    r = await fetch(API + path, { credentials: 'include', ...opts,
      headers: { ...(typeof opts.body === 'string' ? { 'Content-Type': 'application/json' } : {}), ...opts.headers } })
  } catch { throw Object.assign(new Error('Cannot reach the server. Is `python app.py` running on ' + API + '?'), { status: 0 }) }
  const j = await r.json().catch(() => ({ error: 'Unexpected server response' }))
  if (!r.ok) {
    if (r.status === 401 && !path.startsWith('/api/auth/')) window.dispatchEvent(new Event('auth-expired'))
    throw Object.assign(new Error(j.error || 'Request failed'), { status: r.status, data: j })
  }
  return j
}
