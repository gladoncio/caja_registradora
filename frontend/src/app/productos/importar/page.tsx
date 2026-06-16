'use client'
import { useState, useRef } from 'react'
import {
  Box, Card, CardContent, Typography, Button, CircularProgress, Fade, Alert, Grid,
} from '@mui/material'
import { Upload, Download } from '@mui/icons-material'
import api from '@/lib/api'

export default function ImportarProductosPage() {
  const [loading, setLoading] = useState(false)
  const [msg, setMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)

  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setLoading(true)
    setMsg(null)
    try {
      const form = new FormData()
      form.append('file', file)
      await api.post('/productos/importar/', form)
      setMsg({ type: 'success', text: 'Productos importados exitosamente' })
    } catch { setMsg({ type: 'error', text: 'Error al importar' }) }
    finally { setLoading(false) }
  }

  const handleExport = async () => {
    setLoading(true)
    try {
      const res = await api.get('/productos/exportar/', { responseType: 'blob' })
      const url = URL.createObjectURL(res.data)
      const a = document.createElement('a')
      a.href = url; a.download = 'productos.xlsx'; a.click()
      setMsg({ type: 'success', text: 'Exportación completada' })
    } catch { setMsg({ type: 'error', text: 'Error al exportar' }) }
    finally { setLoading(false) }
  }

  return (
    <Fade in timeout={300}>
      <Box>
        <Typography variant="h4" fontWeight={700} mb={3}>Importar / Exportar Productos</Typography>
        {msg && <Alert severity={msg.type} sx={{ mb: 2, borderRadius: 2 }}>{msg.text}</Alert>}
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Card sx={{ borderRadius: 3, textAlign: 'center', py: 4 }}>
              <CardContent>
                <Upload sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" fontWeight={600} gutterBottom>Importar desde Excel</Typography>
                <Typography variant="body2" color="text.secondary" mb={2}>Selecciona un archivo .xlsx con productos</Typography>
                <input ref={fileRef} type="file" accept=".xlsx" onChange={handleImport} style={{ display: 'none' }} />
                <Button variant="contained" onClick={() => fileRef.current?.click()} disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} /> : <Upload />} sx={{ borderRadius: 2, px: 4 }}>
                  Seleccionar archivo
                </Button>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card sx={{ borderRadius: 3, textAlign: 'center', py: 4 }}>
              <CardContent>
                <Download sx={{ fontSize: 48, color: 'secondary.main', mb: 2 }} />
                <Typography variant="h6" fontWeight={600} gutterBottom>Exportar a Excel</Typography>
                <Typography variant="body2" color="text.secondary" mb={2}>Descarga todos los productos en un archivo .xlsx</Typography>
                <Button variant="contained" color="secondary" onClick={handleExport} disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} /> : <Download />} sx={{ borderRadius: 2, px: 4 }}>
                  Exportar Productos
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    </Fade>
  )
}
