import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authAPI, getToken, getUser, clearToken, clearUser, User } from '../services/api'

interface AuthCtx {
  user: User | null
  token: string
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (name: string, email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthCtx | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser]       = useState<User | null>(getUser())
  const [token, setToken2]    = useState(getToken())
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (token && !user) {
      authAPI.me().then(setUser).catch(() => { clearToken(); clearUser(); setToken2('') })
    }
  }, [])

  const login = async (email: string, password: string) => {
    setLoading(true)
    try {
      const { token: t, user: u } = await authAPI.login(email, password)
      setToken2(t); setUser(u)
    } finally { setLoading(false) }
  }

  const register = async (name: string, email: string, password: string) => {
    setLoading(true)
    try {
      const { token: t, user: u } = await authAPI.register(name, email, password)
      setToken2(t); setUser(u)
    } finally { setLoading(false) }
  }

  const logout = async () => {
    await authAPI.logout()
    setUser(null); setToken2('')
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, register, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
