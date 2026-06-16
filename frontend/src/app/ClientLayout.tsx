'use client'
import { useState, useEffect } from 'react'
import { AuthProvider, useAuth } from '@/contexts/AuthContext'
import ThemeRegistry from '@/components/ThemeRegistry'
import Layout from '@/components/Layout'
import { CircularProgress, Box, GlobalStyles } from '@mui/material'

function AppContent({ children }: { children: React.ReactNode }) {
  const { loading } = useAuth()
  const [fontSize, setFontSize] = useState(16)

  useEffect(() => {
    try {
      const saved = localStorage.getItem('app-font-size')
      if (saved) setFontSize(parseInt(saved) || 16)
      const primary = localStorage.getItem('app-primary-color') || '#6366f1'
      const secondary = localStorage.getItem('app-secondary-color') || '#10b981'
      document.documentElement.style.setProperty('--app-primary', primary)
      document.documentElement.style.setProperty('--app-secondary', secondary)
    } catch {}
    const handler = () => {
      try {
        const s = localStorage.getItem('app-font-size')
        if (s) setFontSize(parseInt(s) || 16)
        const p = localStorage.getItem('app-primary-color') || '#6366f1'
        const sc = localStorage.getItem('app-secondary-color') || '#10b981'
        document.documentElement.style.setProperty('--app-primary', p)
        document.documentElement.style.setProperty('--app-secondary', sc)
      } catch {}
    }
    window.addEventListener('storage', handler)
    window.addEventListener('fontsizechange', handler)
    return () => {
      window.removeEventListener('storage', handler)
      window.removeEventListener('fontsizechange', handler)
    }
  }, [])

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    )
  }
  return (
    <>
      <GlobalStyles styles={{ 'html': { fontSize: `${fontSize}px !important` } }} />
      <Layout>{children}</Layout>
    </>
  )
}

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  return (
    <ThemeRegistry>
      <AuthProvider>
        <AppContent>{children}</AppContent>
      </AuthProvider>
    </ThemeRegistry>
  )
}
