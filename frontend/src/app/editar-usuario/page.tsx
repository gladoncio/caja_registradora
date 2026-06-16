'use client'
import { useState, useEffect } from 'react'
import {
  Box, Card, CardContent, Typography, TextField, Button, Grid, CircularProgress,
  Fade, Alert, Avatar, Chip, FormControl, InputLabel, Select, MenuItem,
} from '@mui/material'
import { Person } from '@mui/icons-material'
import api from '@/lib/api'
import { useAuth } from '@/contexts/AuthContext'
import { useTheme, alpha } from '@mui/material'

export default function EditarUsuarioPage() {
  const { user, login } = useAuth()
  const theme = useTheme()

  const [form, setForm] = useState({ username: '', email: '', rut: '' })
  const [loading, setLoading] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    if (user) setForm({ username: user.username, email: user.email || '', rut: user.rut || '' })
  }, [user])

  const handleSave = async () => {
    setLoading(true)
    try {
      await api.put(`/usuarios/${user!.id}/`, form)
      setSaved(true)
    } catch {}
    finally { setLoading(false) }
  }

  return (
    <Fade in timeout={300}>
      <Box>
        <Typography variant="h4" fontWeight={700} mb={3}>Mi Perfil</Typography>
        {saved && <Alert severity="success" sx={{ mb: 2, borderRadius: 2 }} onClose={() => setSaved(false)}>Perfil actualizado</Alert>}
        <Card sx={{ borderRadius: 3 }}>
          <CardContent sx={{ p: 3, textAlign: 'center' }}>
            <Avatar sx={{ width: 72, height: 72, mx: 'auto', mb: 2, bgcolor: 'primary.main', fontSize: 28 }}>
              {user?.username?.charAt(0).toUpperCase()}
            </Avatar>
            <Chip label={user?.permisos} color="primary" size="small" sx={{ mb: 3 }} />
            <Grid container spacing={2} sx={{ textAlign: 'left' }}>
              <Grid item xs={12} sm={6}>
                <TextField fullWidth size="small" label="Usuario" value={form.username}
                  onChange={(e) => setForm({ ...form, username: e.target.value })}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField fullWidth size="small" label="Email" value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField fullWidth size="small" label="RUT" value={form.rut}
                  onChange={(e) => setForm({ ...form, rut: e.target.value })}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
              </Grid>
            </Grid>
            <Button variant="contained" onClick={handleSave} disabled={loading} sx={{ mt: 3, px: 4, borderRadius: 2 }}>
              {loading ? 'Guardando...' : 'Guardar Cambios'}
            </Button>
          </CardContent>
        </Card>
      </Box>
    </Fade>
  )
}
