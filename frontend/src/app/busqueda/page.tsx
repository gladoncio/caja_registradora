'use client'
import { useState, useEffect, useCallback } from 'react'
import {
  Box, Card, CardContent, TextField, Typography, List, ListItemButton,
  ListItemText, Chip, CircularProgress, Fade, InputAdornment,
} from '@mui/material'
import { Search } from '@mui/icons-material'
import { productosAPI } from '@/lib/api'
import { Producto } from '@/types'

export default function BusquedaPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<Producto[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!query.trim()) { setResults([]); return }
    const t = setTimeout(async () => {
      setLoading(true)
      try { const r = await productosAPI.list({ search: query }); setResults(r.data.results || r.data) }
      finally { setLoading(false) }
    }, 300)
    return () => clearTimeout(t)
  }, [query])

  return (
    <Fade in timeout={300}>
      <Box>
        <Typography variant="h4" fontWeight={700} mb={3}>Buscador de Precios</Typography>
        <Card sx={{ borderRadius: 3 }}>
          <CardContent sx={{ p: 3 }}>
            <TextField fullWidth placeholder="Buscar producto por nombre o código..."
              value={query} onChange={(e) => setQuery(e.target.value)} autoFocus
              InputProps={{
                startAdornment: <InputAdornment position="start"><Search color="action" /></InputAdornment>,
                sx: { borderRadius: 2, fontSize: '1.1rem' },
              }} sx={{ mb: 2 }} />
            {loading && <Box textAlign="center" py={4}><CircularProgress /></Box>}
            {!loading && results.length === 0 && query && (
              <Typography color="text.secondary" textAlign="center" py={4}>Sin resultados</Typography>
            )}
            <List>
              {results.map((p) => (
                <ListItemButton key={p.id_producto} sx={{ borderRadius: 2, mb: 0.5 }}>
                  <ListItemText
                    primary={<Typography fontWeight={600}>{p.nombre}</Typography>}
                    secondary={
                      <Box display="flex" gap={1} mt={0.5}>
                        <Chip label={`$${parseInt(p.precio).toLocaleString('es-CL')}`} size="small" color="primary" />
                        <Chip label={p.codigo_barras || 'sin código'} size="small" variant="outlined" />
                        {p.departamento_nombre && <Chip label={p.departamento_nombre} size="small" variant="outlined" />}
                      </Box>
                    }
                  />
                </ListItemButton>
              ))}
            </List>
          </CardContent>
        </Card>
      </Box>
    </Fade>
  )
}
