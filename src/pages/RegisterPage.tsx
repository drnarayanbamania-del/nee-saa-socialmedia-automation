import { useState } from 'react'
import { useAuth } from '../context/AuthContext'

export default function RegisterPage({ onSwitch }: { onSwitch: () => void }) {
  const { register, loading } = useAuth()
  const [name, setName]           = useState('')
  const [email, setEmail]         = useState('')
  const [password, setPassword]   = useState('')
  const [confirm, setConfirm]     = useState('')
  const [error, setError]         = useState('')

  const handle = async (e: React.FormEvent) => {
    e.preventDefault(); setError('')
    if (password !== confirm) { setError('Passwords do not match'); return }
    if (password.length < 6)  { setError('Password must be at least 6 characters'); return }
    try { await register(name, email, password) }
    catch (err: unknown) { setError(err instanceof Error ? err.message : 'Registration failed') }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-950 via-purple-900 to-indigo-950 flex items-center justify-center p-4">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-fuchsia-500/20 rounded-full blur-3xl animate-pulse"/>
        <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-violet-500/20 rounded-full blur-3xl animate-pulse delay-1000"/>
      </div>

      <div className="relative w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-500 to-fuchsia-600 shadow-2xl mb-4">
            <span className="text-2xl">🎬</span>
          </div>
          <h1 className="text-3xl font-black text-white">Bamania's Cine AI</h1>
          <p className="text-violet-300 text-sm mt-1">Create your free account</p>
        </div>

        <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-3xl p-8 shadow-2xl">
          <h2 className="text-xl font-bold text-white mb-6">Get started free 🚀</h2>

          {error && (
            <div className="bg-red-500/20 border border-red-500/50 text-red-200 text-sm rounded-xl p-3 mb-4">
              {error}
            </div>
          )}

          <form onSubmit={handle} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-violet-200 mb-1.5">Full Name</label>
              <input type="text" value={name} onChange={e => setName(e.target.value)} required
                className="w-full bg-white/10 border border-white/20 text-white placeholder-white/40 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400"
                placeholder="Your full name"/>
            </div>
            <div>
              <label className="block text-sm font-medium text-violet-200 mb-1.5">Email</label>
              <input type="email" value={email} onChange={e => setEmail(e.target.value)} required
                className="w-full bg-white/10 border border-white/20 text-white placeholder-white/40 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400"
                placeholder="you@example.com"/>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-violet-200 mb-1.5">Password</label>
                <input type="password" value={password} onChange={e => setPassword(e.target.value)} required
                  className="w-full bg-white/10 border border-white/20 text-white placeholder-white/40 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400"
                  placeholder="Min 6 chars"/>
              </div>
              <div>
                <label className="block text-sm font-medium text-violet-200 mb-1.5">Confirm</label>
                <input type="password" value={confirm} onChange={e => setConfirm(e.target.value)} required
                  className="w-full bg-white/10 border border-white/20 text-white placeholder-white/40 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400"
                  placeholder="Repeat"/>
              </div>
            </div>

            <button type="submit" disabled={loading}
              className="w-full bg-gradient-to-r from-violet-500 to-fuchsia-600 text-white font-bold py-3.5 rounded-xl hover:opacity-90 active:scale-95 transition-all disabled:opacity-50 shadow-lg shadow-violet-500/30">
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"/>
                  Creating account...
                </span>
              ) : 'Create Free Account →'}
            </button>
          </form>

          <p className="text-center text-sm text-violet-300 mt-4">
            Already have an account?{' '}
            <button onClick={onSwitch} className="text-white font-semibold hover:text-violet-200 underline">
              Sign in
            </button>
          </p>
        </div>

        <div className="flex flex-wrap justify-center gap-2 mt-6">
          {['✅ Free 50 Credits','🎬 4K Videos','📱 Auto Publish','🇮🇳 Hindi AI'].map(f => (
            <span key={f} className="text-xs text-violet-300 bg-white/5 border border-white/10 rounded-full px-3 py-1">{f}</span>
          ))}
        </div>
      </div>
    </div>
  )
}
