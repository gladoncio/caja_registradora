'use client'
import { useState } from 'react'
import {
  Box, Card, CardContent, Typography, Button, CircularProgress, Fade, Alert,
} from '@mui/material'
import { Casino, Check } from '@mui/icons-material'
import AuthorizationDialog from '@/components/AuthorizationDialog'
import { autorizacionAPI } from '@/lib/api'

export default function AbrirCajaPage() {
  const [loading, setLoading] = useState(false)
  const [msg, setMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
  const [authOpen, setAuthOpen] = useState(false)

  const handleOpen = async (clave: string) => {
    setLoading(true)
    setMsg(null)
    try {
      const res = await autorizacionAPI.abrirCajon(clave)
      setMsg({ type: 'success', text: res.data.mensaje || 'Cajón abierto' })
    } catch (err: any) {
      setMsg({ type: 'error', text: err.response?.data?.error || 'Error al abrir cajón' })
    } finally { setLoading(false) }
  }

  return (
    <Fade in timeout={300}>
      <Box>
        <Typography variant="h4" fontWeight={700} mb={3}>Abrir Caja</Typography>
        {msg && <Alert severity={msg.type} sx={{ mb: 2, borderRadius: 2 }}>{msg.text}</Alert>}
        <Card sx={{ borderRadius: 3, textAlign: 'center', py: 6 }}>
          <CardContent>
            <Box sx={{ width: 80, height: 80, borderRadius: '50%', mx: 'auto', mb: 2, display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: (theme: any) => `${theme.palette.warning.main}15` }}>
              <Casino sx={{ fontSize: 40, color: 'warning.main' }} />
            </Box>
            <Typography variant="h5" fontWeight={700} mb={1}>Abrir Cajón de Dinero</Typography>
            <Typography variant="body2" color="text.secondary" mb={4}>Se requiere autorización con clave de anulación</Typography>
            <Button variant="contained" size="large" color="warning" onClick={() => setAuthOpen(true)}
              disabled={loading} startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <Casino />}
              sx={{ px: 6, py: 1.5, borderRadius: 3, fontSize: '1.1rem' }}>
              {loading ? 'Abriendo...' : 'Abrir Cajón'}
            </Button>
          </CardContent>
        </Card>
        <AuthorizationDialog open={authOpen} onClose={() => setAuthOpen(false)}
          onSuccess={(_u: string, clave: string) => handleOpen(clave)}
          titulo="Abrir Cajón" mensaje="Ingresa tu clave de anulación" accion="Abrir" icono={<Casino />} />
      </Box>
    </Fade>
  )
}
