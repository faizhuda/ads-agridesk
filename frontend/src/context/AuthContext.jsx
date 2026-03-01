import { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext(null)

function decodeJWT(token) {
  try {
    const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
    return JSON.parse(atob(base64))
  } catch {
    return null
  }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('agridesk_token') || '')
  const [user, setUser] = useState(() => {
    const t = localStorage.getItem('agridesk_token')
    return t ? decodeJWT(t) : null
  })

  function login(accessToken) {
    localStorage.setItem('agridesk_token', accessToken)
    setToken(accessToken)
    setUser(decodeJWT(accessToken))
  }

  function logout() {
    localStorage.removeItem('agridesk_token')
    setToken('')
    setUser(null)
  }

  const value = {
    token,
    user,
    isLoggedIn: !!user,
    role: user?.role || null,
    name: user?.name || user?.email || '',
    userId: user?.sub || null,
    login,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be inside AuthProvider')
  return ctx
}
