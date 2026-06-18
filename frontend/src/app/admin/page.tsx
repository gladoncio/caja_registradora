'use client'
import { useState, useEffect } from 'react'
import { Box, Card, CardContent, Typography, Grid, Chip, alpha, Fade, CircularProgress } from '@mui/material'
import { useTheme } from '@mui/material'
import { useRouter } from 'next/navigation'
import api from '@/lib/api'

const ADMIN_LINKS = [
  { label: 'Configuración', href: '/admin/configuracion', icon: '⚙️', perm: 'ver_configuracion', desc: 'Sistema, moneda, redondeo, debug' },
  { label: 'Monedas', href: '/admin/monedas', icon: '💰', perm: 'gestionar_monedas', desc: 'Administrar monedas y tasas de cambio' },
  { label: 'Métodos de Pago', href: '/admin/metodos-pago', icon: '💳', perm: 'gestionar_metodos_pago', desc: 'Configurar métodos de pago' },
  { label: 'Usuarios', href: '/admin/usuarios', icon: '👥', perm: 'gestionar_usuarios', desc: 'Gestionar usuarios y roles' },
  { label: 'Logs', href: '/admin/logs', icon: '📋', perm: 'ver_logs', desc: 'Registro de eventos del sistema' },
  { label: 'Actualizaciones', href: '/admin/actualizaciones', icon: '🔄', perm: 'ver_actualizaciones', desc: 'Verificar nuevas versiones' },
  { label: 'Atajos', href: '/admin/atajos', icon: '⌨️', perm: 'ver_configuracion', desc: 'Configurar atajos de teclado' },
]

export default function AdminPage() {
  const theme = useTheme()
  const router = useRouter()
  const [permisos, setPermisos] = useState<string[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/me/').then(r => setPermisos(r.data.permisos_usuario || [])).catch(() => {}).finally(() => setLoading(false))
  }, [])

  if (loading) return <Box display="flex" justifyContent="center" py={6}><CircularProgress /></Box>

  return (
    <Fade in timeout={300}>
      <Box>
        <Typography variant="h4" fontWeight={700} mb={3}>Panel de Administración</Typography>
        <Grid container spacing={2}>
          {ADMIN_LINKS.filter(l => permisos.includes(l.perm)).map(link => (
            <Grid item xs={12} sm={6} md={4} key={link.href}>
              <Card onClick={() => router.push(link.href)} sx={{
                borderRadius: 3, cursor: 'pointer', transition: 'all 0.15s',
                '&:hover': { transform: 'translateY(-2px)', boxShadow: 4 },
              }}>
                <CardContent sx={{ p: 2.5 }}>
                  <Typography variant="h4" mb={1}>{link.icon}</Typography>
                  <Typography variant="h6" fontWeight={700}>{link.label}</Typography>
                  <Typography variant="body2" color="text.secondary">{link.desc}</Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Fade>
  )
}
