'use client'
import { useState } from 'react'
import {
  Dialog, DialogTitle, DialogContent, DialogActions, TextField, Button,
  Typography, Box, Alert, InputAdornment, IconButton, CircularProgress, Zoom,
} from '@mui/material'
import { Lock, Visibility, VisibilityOff, Check, Casino } from '@mui/icons-material'
import { autorizacionAPI } from '@/lib/api'
import { useTheme } from '@mui/material'

interface AuthDialogProps {
  open: boolean
  onClose: () => void
  onSuccess: (usuario: string, clave: string) => void
  titulo?: string
  mensaje?: string
  accion?: string
  icono?: React.ReactNode
}

export default function AuthorizationDialog({
  open, onClose, onSuccess,
  titulo = 'Autorización requerida',
  mensaje = 'Ingresa tu clave de anulación',
  accion = 'Autorizar',
  icono,
}: AuthDialogProps) {
  const theme = useTheme()
  const [clave, setClave] = useState('')
  const [showClave, setShowClave] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!clave.trim()) { setError('Ingresa una clave'); return }
    setLoading(true)
    setError('')
    try {
      const res = await autorizacionAPI.verificarClave(clave.trim())
      if (res.data.valida) {
        const tmp = clave.trim()
        setClave('')
        onClose()
        onSuccess(res.data.usuario, tmp)
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Clave inválida')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth
      PaperProps={{ sx: { borderRadius: 4 } }} TransitionComponent={Zoom}>
      <form onSubmit={handleSubmit}>
        <DialogTitle sx={{ pb: 0 }}>
          <Box display="flex" alignItems="center" gap={1.5}>
            <Box sx={{
              width: 44, height: 44, borderRadius: 2,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              background: `linear-gradient(135deg, ${theme.palette.warning.main}, ${theme.palette.warning.dark})`,
              color: '#fff',
            }}>
              {icono || <Lock />}
            </Box>
            <Box>
              <Typography variant="h6" fontWeight={700}>{titulo}</Typography>
              <Typography variant="caption" color="text.secondary">{mensaje}</Typography>
            </Box>
          </Box>
        </DialogTitle>
        <DialogContent sx={{ pt: 3 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>
              {error}
            </Alert>
          )}
          <TextField
            fullWidth
            label="Clave de anulación"
            value={clave}
            onChange={(e) => { setClave(e.target.value); setError('') }}
            type={showClave ? 'text' : 'password'}
            autoFocus
            InputProps={{
              startAdornment: <InputAdornment position="start"><Lock color="action" fontSize="small" /></InputAdornment>,
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton onClick={() => setShowClave(!showClave)} edge="end" size="small">
                    {showClave ? <VisibilityOff fontSize="small" /> : <Visibility fontSize="small" />}
                  </IconButton>
                </InputAdornment>
              ),
              sx: { borderRadius: 2, fontSize: '1.2rem', letterSpacing: 4 },
            }}
            sx={{ mb: 1 }}
          />
        </DialogContent>
        <DialogActions sx={{ p: 3, pt: 0, gap: 1 }}>
          <Button onClick={onClose} variant="outlined" sx={{ borderRadius: 2, px: 3 }}>
            Cancelar
          </Button>
          <Button type="submit" variant="contained" disabled={loading}
            startIcon={loading ? <CircularProgress size={18} color="inherit" /> : <Check />}
            sx={{ borderRadius: 2, px: 4 }}>
            {loading ? 'Verificando...' : accion}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  )
}

export async function solicitarClave(
  titulo?: string,
  mensaje?: string,
  accion?: string,
): Promise<string | null> {
  return new Promise((resolve) => {
    const dialog = document.createElement('div')
    dialog.id = 'auth-dialog-container'
    document.body.appendChild(dialog)

    const handleClose = () => {
      document.body.removeChild(dialog)
      resolve(null)
    }
    const handleSuccess = (usuario: string) => {
      document.body.removeChild(dialog)
      resolve(usuario)
    }

    // This is a simplified version - in a real app, use a proper state management solution
    resolve(null)
  })
}
