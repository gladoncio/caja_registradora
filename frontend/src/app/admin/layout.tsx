'use client'
import { useEffect, useState } from 'react'
import { Box, Typography, CircularProgress, Button } from '@mui/material'
import { useRouter, usePathname } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import api from '@/lib/api'

const ADMIN_PERMS = [
  'ver_configuracion', 'gestionar_usuarios', 'gestionar_monedas',
  'gestionar_metodos_pago', 'ver_logs', 'ver_actualizaciones',
]

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const { user, loading: authLoading } = useAuth()
  const router = useRouter()
  const pathname = usePathname()
  const [checking, setChecking] = useState(true)
  const [hasAccess, setHasAccess] = useState(false)

  useEffect(() => {
    if (authLoading) return
    if (!user) { router.push('/login'); return }
    api.get('/me/').then(r => {
      const perms = r.data.permisos_usuario || []
      const hasAny = perms.some((p: string) => ADMIN_PERMS.includes(p))
      setHasAccess(hasAny)
    }).catch(() => setHasAccess(false)).finally(() => setChecking(false))
  }, [user, authLoading, router])

  if (authLoading || checking) {
    return <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh"><CircularProgress /></Box>
  }

  if (!hasAccess) {
    return (
      <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" minHeight="60vh" gap={2}>
        <Typography variant="h5" fontWeight={700} color="error">Acceso denegado</Typography>
        <Typography color="text.secondary">No tienes permisos para acceder a esta sección</Typography>
        <Button variant="contained" onClick={() => router.push('/caja/1')} sx={{ borderRadius: 2 }}>
          Volver a la caja
        </Button>
      </Box>
    )
  }

  return <>{children}</>
}
