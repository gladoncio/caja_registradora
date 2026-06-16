'use client'
import { useState } from 'react'
import {
  Box, Card, CardContent, Typography, Button, CircularProgress, Fade,
  Alert, TextField,
} from '@mui/material'
import { QrCode } from '@mui/icons-material'
import api from '@/lib/api'

export default function GenerarCodigoPage() {
  const [loading, setLoading] = useState(false)
  const [imgUrl, setImgUrl] = useState('')
  const [error, setError] = useState('')

  const generate = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await api.get('/generar_codigo_ean13/', { responseType: 'blob' })
      const url = URL.createObjectURL(res.data)
      setImgUrl(url)
    } catch { setError('Error al generar código') }
    finally { setLoading(false) }
  }

  return (
    <Fade in timeout={300}>
      <Box>
        <Typography variant="h4" fontWeight={700} mb={3}>Generar Código de Barras</Typography>
        {error && <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>{error}</Alert>}
        <Card sx={{ borderRadius: 3, textAlign: 'center', py: 4 }}>
          <CardContent>
            <Button variant="contained" onClick={generate} disabled={loading} startIcon={loading ? <CircularProgress size={20} /> : <QrCode />} sx={{ px: 4, py: 1.5, borderRadius: 3 }}>
              {loading ? 'Generando...' : 'Generar Código EAN-13'}
            </Button>
            {imgUrl && <Box mt={3}><img src={imgUrl} alt="Código de barras" style={{ maxWidth: 300 }} /></Box>}
          </CardContent>
        </Card>
      </Box>
    </Fade>
  )
}
