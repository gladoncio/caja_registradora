'use client'
import { useState } from 'react'
import {
  Box, Card, CardContent, Typography, Button, CircularProgress, Fade, Alert,
} from '@mui/material'
import { CreditCard } from '@mui/icons-material'
import api from '@/lib/api'

export default function TarjetaAutorizacionPage() {
  const [loading, setLoading] = useState(false)
  const [imgUrl, setImgUrl] = useState('')

  const generate = async () => {
    setLoading(true)
    try {
      const res = await api.get('/generate_barcode/', { responseType: 'blob' })
      setImgUrl(URL.createObjectURL(res.data))
    } catch { }
    finally { setLoading(false) }
  }

  return (
    <Fade in timeout={300}>
      <Box>
        <Typography variant="h4" fontWeight={700} mb={3}>Tarjeta de Autorización</Typography>
        <Card sx={{ borderRadius: 3, textAlign: 'center', py: 4 }}>
          <CardContent>
            <Button variant="contained" onClick={generate} disabled={loading} startIcon={loading ? <CircularProgress size={20} /> : <CreditCard />} sx={{ px: 4, py: 1.5, borderRadius: 3 }}>
              Generar Tarjeta
            </Button>
            {imgUrl && <Box mt={3}><img src={imgUrl} alt="Tarjeta de autorización" style={{ maxWidth: 300 }} /></Box>}
          </CardContent>
        </Card>
      </Box>
    </Fade>
  )
}
