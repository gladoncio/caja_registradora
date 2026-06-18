'use client'
import { useEffect } from 'react'
import { Box, Typography, Paper, Fade, alpha, useTheme } from '@mui/material'
import { CheckCircle, Error as ErrorIcon } from '@mui/icons-material'

export default function BigAlert({ open, message, severity, onClose }: {
  open: boolean; message: string; severity: 'success' | 'error' | 'info'; onClose: () => void
}) {
  const theme = useTheme()
  const colors = {
    success: { bg: '#065f46', icon: <CheckCircle sx={{ fontSize: 48 }} />, border: alpha(theme.palette.success.main, 0.3) },
    error: { bg: '#991b1b', icon: <ErrorIcon sx={{ fontSize: 48 }} />, border: alpha(theme.palette.error.main, 0.3) },
    info: { bg: '#1e40af', icon: <CheckCircle sx={{ fontSize: 48 }} />, border: alpha(theme.palette.info.main, 0.3) },
  }
  const c = colors[severity]

  useEffect(() => {
    if (open) {
      const t = setTimeout(onClose, 2500)
      return () => clearTimeout(t)
    }
  }, [open, onClose])

  if (!open) return null

  return (
    <Box sx={{
      position: 'fixed', inset: 0, zIndex: 99999,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      bgcolor: 'rgba(0,0,0,0.4)',
      animation: 'fadeIn 0.15s ease',
    }} onClick={onClose}>
      <Paper elevation={24} sx={{
        p: 4, borderRadius: 4, textAlign: 'center', maxWidth: 400, width: '90%',
        bgcolor: c.bg, color: '#fff',
        border: 2, borderColor: c.border,
        boxShadow: `0 20px 60px ${alpha('#000', 0.3)}`,
      }}>
        <Fade in timeout={200}>
          <Box>
            {c.icon}
            <Typography variant="h5" fontWeight={800} mt={2} mb={0.5}>
              {severity === 'success' ? '¡Operación exitosa!' : severity === 'error' ? 'Error' : 'Información'}
            </Typography>
            <Typography variant="body1" sx={{ opacity: 0.9 }}>{message}</Typography>
          </Box>
        </Fade>
      </Paper>
    </Box>
  )
}
