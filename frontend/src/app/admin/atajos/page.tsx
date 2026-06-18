'use client'
import { useState } from 'react'
import {
  Box, Card, CardContent, Typography, TextField, Button, Grid, Chip, Fade,
  Paper, alpha, Alert, Divider,
} from '@mui/material'
import { Keyboard, Save, RestartAlt } from '@mui/icons-material'
import { useTheme } from '@mui/material'

interface Atajo {
  id: string
  label: string
  defaultKey: string
  key: string
  grupo: string
}

const DEFAULT_ATAJOS: Atajo[] = [
  { id: 'caja1', label: 'Caja 1', defaultKey: 'F1', key: 'F1', grupo: 'Cajas' },
  { id: 'caja2', label: 'Caja 2', defaultKey: 'F2', key: 'F2', grupo: 'Cajas' },
  { id: 'caja3', label: 'Caja 3', defaultKey: 'F3', key: 'F3', grupo: 'Cajas' },
  { id: 'caja4', label: 'Caja 4', defaultKey: 'F4', key: 'F4', grupo: 'Cajas' },
  { id: 'caja5', label: 'Caja 5', defaultKey: 'F5', key: 'F5', grupo: 'Cajas' },
  { id: 'caja6', label: 'Caja 6', defaultKey: 'F6', key: 'F6', grupo: 'Cajas' },
  { id: 'caja7', label: 'Caja 7', defaultKey: 'F7', key: 'F7', grupo: 'Cajas' },
  { id: 'caja8', label: 'Caja 8', defaultKey: 'F8', key: 'F8', grupo: 'Cajas' },
  { id: 'nuevaCaja', label: 'Nueva Caja', defaultKey: 'F9', key: 'F9', grupo: 'Cajas' },
  { id: 'cobrar', label: 'Cobrar', defaultKey: 'F10', key: 'F10', grupo: 'POS' },
  { id: 'abrirCajon', label: 'Abrir Cajón', defaultKey: 'Ctrl+D', key: 'Ctrl+D', grupo: 'POS' },
  { id: 'rapidoPrefijo', label: 'Prefijo rápido', defaultKey: '-', key: '-', grupo: 'Rápidos' },
  { id: 'rapido0', label: 'Rápido #0', defaultKey: '0', key: '0', grupo: 'Rápidos' },
  { id: 'rapido1', label: 'Rápido #1', defaultKey: '1', key: '1', grupo: 'Rápidos' },
  { id: 'rapido2', label: 'Rápido #2', defaultKey: '2', key: '2', grupo: 'Rápidos' },
  { id: 'rapido3', label: 'Rápido #3', defaultKey: '3', key: '3', grupo: 'Rápidos' },
  { id: 'rapido4', label: 'Rápido #4', defaultKey: '4', key: '4', grupo: 'Rápidos' },
  { id: 'rapido5', label: 'Rápido #5', defaultKey: '5', key: '5', grupo: 'Rápidos' },
  { id: 'rapido6', label: 'Rápido #6', defaultKey: '6', key: '6', grupo: 'Rápidos' },
  { id: 'rapido7', label: 'Rápido #7', defaultKey: '7', key: '7', grupo: 'Rápidos' },
  { id: 'rapido8', label: 'Rápido #8', defaultKey: '8', key: '8', grupo: 'Rápidos' },
  { id: 'rapido9', label: 'Rápido #9', defaultKey: '9', key: '9', grupo: 'Rápidos' },
]

const GRUPOS = ['Cajas', 'POS', 'Rápidos']

export default function ConfigurarAtajosPage() {
  const theme = useTheme()
  const [atajos, setAtajos] = useState<Atajo[]>(() => {
    try {
      const saved = localStorage.getItem('shortcuts-config')
      if (saved) {
        const parsed = JSON.parse(saved)
        return DEFAULT_ATAJOS.map(a => ({ ...a, key: parsed[a.id] || a.key }))
      }
    } catch {}
    return DEFAULT_ATAJOS
  })
  const [editing, setEditing] = useState<string | null>(null)
  const [saved, setSaved] = useState(false)

  const handleKeyCapture = (id: string, e: React.KeyboardEvent) => {
    e.preventDefault()
    e.stopPropagation()
    const parts: string[] = []
    if (e.ctrlKey) parts.push('Ctrl')
    if (e.shiftKey) parts.push('Shift')
    if (e.key && !['Control', 'Shift', 'Alt'].includes(e.key)) {
      parts.push(e.key.length === 1 ? e.key.toUpperCase() : e.key)
    }
    const key = parts.join('+')
    if (key) {
      setAtajos(prev => prev.map(a => a.id === id ? { ...a, key } : a))
      setEditing(null)
    }
  }

  const handleSave = () => {
    const map: Record<string, string> = {}
    atajos.forEach(a => { map[a.id] = a.key })
    localStorage.setItem('shortcuts-config', JSON.stringify(map))
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const handleReset = () => {
    setAtajos(DEFAULT_ATAJOS)
    localStorage.removeItem('shortcuts-config')
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <Fade in timeout={300}>
      <Box>
        <Box display="flex" alignItems="center" gap={1.5} mb={3}>
          <Keyboard color="primary" />
          <Box>
            <Typography variant="h4" fontWeight={700}>Configurar Atajos</Typography>
            <Typography variant="caption" color="text.secondary">Personaliza las teclas de acceso rápido</Typography>
          </Box>
        </Box>

        {saved && <Alert severity="success" sx={{ mb: 2, borderRadius: 2 }}>Atajos guardados</Alert>}

        <Card sx={{ borderRadius: 3 }}>
          <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
            {GRUPOS.map(grupo => (
              <Box key={grupo} mb={3}>
                <Typography variant="subtitle2" fontWeight={700} color="primary.main" mb={1}>{grupo}</Typography>
                <Grid container spacing={1}>
                  {atajos.filter(a => a.grupo === grupo).map(atajo => (
                    <Grid item xs={12} sm={6} md={4} key={atajo.id}>
                      <Paper
                        elevation={0}
                        onDoubleClick={() => setEditing(atajo.id)}
                        onKeyDown={(e) => editing === atajo.id && handleKeyCapture(atajo.id, e as any)}
                        tabIndex={0}
                        sx={{
                          p: 1.5, borderRadius: 2, border: 2,
                          borderColor: editing === atajo.id ? 'primary.main' : 'divider',
                          bgcolor: editing === atajo.id ? alpha(theme.palette.primary.main, 0.04) : 'transparent',
                          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                          cursor: 'pointer',
                          '&:hover': { borderColor: 'primary.light' },
                          outline: 'none',
                        }}>
                        <Typography variant="body2">{atajo.label}</Typography>
                        {editing === atajo.id ? (
                          <Chip label="Presiona tecla..." size="small" color="warning" sx={{ fontWeight: 700, fontFamily: 'monospace' }} />
                        ) : (
                          <Chip
                            label={atajo.key}
                            size="small"
                            variant={atajo.key !== atajo.defaultKey ? 'filled' : 'outlined'}
                            color={atajo.key !== atajo.defaultKey ? 'primary' : 'default'}
                            sx={{ fontWeight: 700, fontFamily: 'monospace', cursor: 'pointer' }}
                            onClick={() => setEditing(atajo.id)}
                          />
                        )}
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              </Box>
            ))}

            <Divider sx={{ my: 2 }} />
            <Typography variant="caption" color="text.secondary" display="block" mb={2}>
              Haz doble clic en un atajo para cambiarlo. Presiona la combinación de teclas deseada.
            </Typography>
            <Box display="flex" gap={1}>
              <Button variant="contained" startIcon={<Save />} onClick={handleSave} sx={{ borderRadius: 2 }}>
                Guardar Atajos
              </Button>
              <Button variant="outlined" startIcon={<RestartAlt />} onClick={handleReset} sx={{ borderRadius: 2 }}>
                Restaurar default
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Fade>
  )
}
