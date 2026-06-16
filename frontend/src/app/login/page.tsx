'use client'
import { useState } from 'react'
import {
  Box, Card, CardContent, TextField, Button, Typography, Alert, CircularProgress,
  InputAdornment, IconButton, alpha,
} from '@mui/material'
import { Visibility, VisibilityOff, Store, Lock, Person } from '@mui/icons-material'
import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const { login, user } = useAuth()
  const router = useRouter()

  if (user) {
    router.push('/caja/1')
    return null
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(username, password)
      router.push('/caja/1')
    } catch {
      setError('Credenciales inválidas')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: (theme) => theme.palette.mode === 'dark'
          ? 'linear-gradient(135deg, #0a1929 0%, #132f4c 50%, #0a1929 100%)'
          : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        p: 2,
      }}
    >
      <Card
        sx={{
          maxWidth: 420, width: '100%',
          overflow: 'visible',
          borderRadius: 4,
          boxShadow: (theme) => theme.palette.mode === 'dark'
            ? '0 20px 60px rgba(0,0,0,0.5)'
            : '0 20px 60px rgba(0,0,0,0.15)',
        }}
      >
        <Box
          sx={{
            display: 'flex', flexDirection: 'column', alignItems: 'center',
            pt: 4, pb: 1, px: 4,
          }}
        >
          <Box
            sx={{
              width: 64, height: 64, borderRadius: 3,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              bgcolor: (theme) => alpha(theme.palette.primary.main, 0.1),
              mb: 2,
            }}
          >
            <Store sx={{ fontSize: 32, color: 'primary.main' }} />
          </Box>
          <Typography variant="h4" fontWeight={800} gutterBottom>
            Caja Registradora
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Inicia sesión para continuar
          </Typography>
        </Box>

        <CardContent sx={{ px: 4, pb: 4 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Usuario"
              variant="outlined"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoFocus
              required
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Person color="action" />
                  </InputAdornment>
                ),
              }}
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Contraseña"
              type={showPassword ? 'text' : 'password'}
              variant="outlined"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Lock color="action" />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={() => setShowPassword(!showPassword)} edge="end" size="small">
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
              sx={{ mb: 3 }}
            />

            <Button
              fullWidth
              type="submit"
              variant="contained"
              size="large"
              disabled={loading}
              sx={{ py: 1.5, fontSize: '1rem' }}
            >
              {loading ? <CircularProgress size={24} color="inherit" /> : 'Ingresar'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </Box>
  )
}
