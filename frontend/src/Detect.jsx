import React, { useEffect, useRef, useState, useCallback } from 'react'
import { Camera, Square, AlertTriangle, Loader2 } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { api, card, btn, ghost, EMOTIONS } from './ui'

const camError = e => ({
  NotAllowedError: 'Camera permission was denied. Allow camera access in the address bar, then try again.',
  NotFoundError: 'No camera was found on this device.',
  NotReadableError: 'The camera is in use by another app. Close it and retry.',
  OverconstrainedError: 'No camera matches the requested settings.' }[e.name] || `Camera error: ${e.message}`)

export default function Detect({ result, onResult, go }) {
  const video = useRef(null), stream = useRef(null), timer = useRef(null), busy = useRef(false)
  const [on, setOn] = useState(false), [status, setStatus] = useState('Camera is off.'), [face, setFace] = useState(null)
  const [sending, setSending] = useState(false), [model, setModel] = useState(null), [fail, setFail] = useState('')

  useEffect(() => { api('/api/model/status').then(setModel).catch(e => setModel({ model_available: false, message: e.message })) }, [])
  const stop = useCallback(() => {
    clearInterval(timer.current); timer.current = null
    stream.current?.getTracks().forEach(t => t.stop()); stream.current = null
    if (video.current) video.current.srcObject = null
    setOn(false); setFace(null); setStatus('Camera is off.')
  }, [])
  useEffect(() => stop, [stop]) // runs on unmount: navigation or logout releases the camera

  const sample = useCallback(async () => {
    const v = video.current
    if (busy.current || !v || v.readyState < 2 || !v.videoWidth) return
    busy.current = true; setSending(true)
    try {
      const w = Math.min(640, v.videoWidth), h = Math.round(w * v.videoHeight / v.videoWidth)
      const c = document.createElement('canvas'); c.width = w; c.height = h
      c.getContext('2d').drawImage(v, 0, 0, w, h)
      const blob = await new Promise(r => c.toBlob(r, 'image/jpeg', 0.85))
      if (!blob) throw new Error('Empty frame')
      const fd = new FormData(); fd.append('image', blob, 'frame.jpg')
      const j = await api('/api/predict', { method: 'POST', body: fd })
      setFace(true); setFail(''); setStatus('Face detected · analysing'); onResult(j)
    } catch (e) {
      if (e.status === 422) { setFace(false); setStatus('No face visible. Face the camera in good light.') }
      else {
        setFail(e.message); setStatus('Detection paused.')
        if (e.status === 503) { setModel({ model_available: false }); clearInterval(timer.current) }
      }
    } finally { busy.current = false; setSending(false) }
  }, [onResult])

  const start = async () => {
    if (stream.current) return
    if (!navigator.mediaDevices?.getUserMedia) return setFail('This browser cannot access the camera. Use Chrome or Edge on http://localhost.')
    setFail(''); setStatus('Requesting camera permission…')
    try {
      const s = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } }, audio: false })
      stream.current = s
      const v = video.current; v.srcObject = s
      await new Promise((res, rej) => {
        if (v.readyState >= 1 && v.videoWidth) return res()
        v.onloadedmetadata = res; setTimeout(() => rej(new Error('Camera started but no video arrived.')), 8000)
      })
      await v.play()
      setOn(true); api('/api/predict/reset', { method: 'POST' }).catch(() => {})
      if (model && !model.model_available) return setStatus('Camera on · CNN unavailable, so detection is disabled.')
      setStatus('Camera on · looking for a face…')
      timer.current = setInterval(sample, 1500)
    } catch (e) { stop(); setFail(camError(e)) }
  }
  const missing = model && !model.model_available
  return (
    <div className="grid gap-5 md:grid-cols-2 rise">
      <div className={card}>
        <div className="relative overflow-hidden rounded-xl bg-black aspect-video">
          <video ref={video} autoPlay muted playsInline className="h-full w-full object-cover -scale-x-100" aria-label="Live camera preview" />
          {!on && <div className="absolute inset-0 grid place-items-center text-white/50"><Camera size={40} /></div>}
          {on && <span className="absolute left-3 top-3 flex items-center gap-2 rounded-full bg-black/60 px-3 py-1 text-xs"><span className="h-2 w-2 animate-pulse rounded-full bg-red-500" />LIVE{sending && <Loader2 size={12} className="animate-spin" />}</span>}
        </div>
        <div className="mt-4 flex gap-2">
          {!on ? <button className={btn} onClick={start}><Camera size={16} />Start detection</button> : <button className={ghost} onClick={stop}><Square size={16} />Stop detection</button>}
        </div>
        <p role="status" className="mt-3 text-sm text-violet-200">{status}</p>
        {on && !missing && <p className="text-xs text-white/50">Face: {face === null ? 'searching' : face ? 'detected' : 'not visible'}</p>}
        {fail && <p role="alert" className="mt-2 flex gap-2 text-sm text-red-300"><AlertTriangle size={16} className="shrink-0" />{fail}</p>}
        <p className="mt-2 text-xs text-white/40">Frames are analysed in memory and never stored.</p>
      </div>
      <div className="space-y-4">
        {missing && <div className={card + ' border-amber-400/30'}><h2 className="font-semibold text-amber-300">CNN unavailable</h2>
          <p className="mt-1 text-sm text-white/70">{model.message || 'No trained model was found, so no predictions can be made.'}</p>
          <pre className="mt-2 overflow-x-auto rounded bg-black/50 p-3 text-xs">{`cd backend\n# put FER-2013 in data/fer2013/train and /test\npython train_model.py --epochs 5\npython evaluate_model.py\n# restart: python app.py`}</pre></div>}
        <div className={card}><h2 className="font-semibold mb-2">Predicted facial expression</h2>
          {result ? <>
            <p className="text-3xl font-bold capitalize text-violet-300">{result.emotion} <span className="text-lg text-white/70">{(result.confidence * 100).toFixed(1)}%</span></p>
            <div className="mt-2 h-2 rounded bg-white/10"><div className="h-2 rounded bg-gradient-to-r from-violet-500 to-fuchsia-500" style={{ width: `${result.confidence * 100}%` }} /></div>
            <div className="mt-3 h-48"><ResponsiveContainer><BarChart data={EMOTIONS.map(e => ({ e, p: +(result.probabilities[e] * 100).toFixed(1) }))}>
              <XAxis dataKey="e" stroke="#aaa" fontSize={11} /><YAxis stroke="#aaa" fontSize={11} /><Tooltip /><Bar dataKey="p" fill="#a78bfa" radius={4} /></BarChart></ResponsiveContainer></div>
            <button className={btn + ' mt-3'} onClick={() => go('music')}>Get music recommendations</button>
          </> : <p className="text-sm text-white/60">No prediction yet. Start detection and face the camera. A prediction is a guess about facial expression, not a diagnosis of feelings.</p>}
        </div>
      </div>
    </div>)
}
