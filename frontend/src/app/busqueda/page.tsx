'use client'
import { useState, useEffect, useCallback } from 'react'
import {
  Box, Card, CardContent, TextField, Typography, Chip, CircularProgress,
  Fade, Paper, alpha, Grid, Dialog, DialogTitle, DialogContent, Button, IconButton,
} from '@mui/material'
import { Search, Close } from '@mui/icons-material'
import { productosAPI, carritoAPI } from '@/lib/api'
import { Producto } from '@/types'
import { useTheme } from '@mui/material'
import BigAlert from '@/components/BigAlert'
import { formatMoney, formatNumber } from '@/lib/format'

export default function BusquedaPage() {
  const theme = useTheme()
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<Producto[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedProduct, setSelectedProduct] = useState<Producto | null>(null)
  const [cartDialog, setCartDialog] = useState(false)
  const [adding, setAdding] = useState(false)
  const [alert, setAlert] = useState<{ msg: string; severity: 'success' | 'error' | 'info' } | null>(null)

  useEffect(() => {
    if (!query.trim()) { setResults([]); return }
    const t = setTimeout(async () => {
      setLoading(true)
      try { const r = await productosAPI.list({ search: query }); setResults(r.data.results || r.data) }
      finally { setLoading(false) }
    }, 300)
    return () => clearTimeout(t)
  }, [query])

  const addToCart = useCallback(async (cartNum: number) => {
    if (!selectedProduct || adding) return
    setAdding(true)
    try {
      const p = selectedProduct
      await carritoAPI.agregar(p.id_producto, 1, cartNum)
      setCartDialog(false)
      setSelectedProduct(null)
      setAlert({ msg: `Agregado a Caja ${cartNum}`, severity: 'success' })
    } catch {
      setAlert({ msg: 'Error al agregar', severity: 'error' })
    } finally { setAdding(false) }
  }, [selectedProduct, adding])

  return (
    <Fade in timeout={300}>
      <Box>
        <BigAlert open={!!alert} message={alert?.msg || ''} severity={alert?.severity || 'info'}
          onClose={() => setAlert(null)} />
        <Typography variant="h4" fontWeight={700} mb={3}>Buscador de Precios</Typography>
        <Card sx={{ borderRadius: 3 }}>
          <CardContent sx={{ p: 3 }}>
            <Paper sx={{
              mb: 2, display: 'flex', alignItems: 'center',
              border: 2, borderColor: alpha(theme.palette.primary.main, 0.15), borderRadius: 3,
              bgcolor: alpha(theme.palette.primary.main, 0.03),
              '&:focus-within': { borderColor: 'primary.main', boxShadow: `0 0 0 4px ${alpha(theme.palette.primary.main, 0.1)}` },
            }}>
              <Box sx={{ px: 1.5, color: 'text.disabled' }}><Search /></Box>
              <TextField fullWidth placeholder="Buscar producto por nombre o código..."
                value={query} onChange={(e) => setQuery(e.target.value)} autoFocus
                variant="standard" InputProps={{ disableUnderline: true }}
                sx={{ '& .MuiInputBase-root': { py: 1.2, fontSize: { xs: '0.9rem', sm: '1rem' } } }} />
            </Paper>
            {loading && <Box textAlign="center" py={4}><CircularProgress /></Box>}
            {!loading && results.length === 0 && query && (
              <Typography color="text.secondary" textAlign="center" py={4}>Sin resultados</Typography>
            )}
            <Grid container spacing={1.5}>
              {results.map((p) => (
                <Grid item xs={12} sm={6} md={4} key={p.id_producto}>
                  <Paper elevation={0} onClick={() => { setSelectedProduct(p); setCartDialog(true) }}
                    sx={{
                      p: 1.5, borderRadius: 2, border: 1, borderColor: 'divider',
                      bgcolor: alpha(theme.palette.grey[500], 0.02), cursor: 'pointer',
                      transition: 'all 0.15s',
                      '&:hover': { borderColor: 'primary.main', bgcolor: alpha(theme.palette.primary.main, 0.04) },
                    }}>
                    <Typography fontWeight={600} noWrap>{p.nombre}</Typography>
                    <Box display="flex" gap={0.5} flexWrap="wrap" mt={0.5}>
                      <Chip label={formatMoney(p.precio)} size="small" color="primary" sx={{ fontWeight: 700 }} />
                      <Chip label={p.tipo_venta} size="small" variant="outlined" sx={{ height: 20 }} />
                      {p.departamento_nombre && <Chip label={p.departamento_nombre} size="small" variant="outlined" sx={{ height: 20 }} />}
                    </Box>
                    {p.codigo_barras && (
                      <Typography variant="caption" color="text.disabled" display="block" mt={0.5}>
                        Código: {p.codigo_barras}
                      </Typography>
                    )}
                    <Typography variant="caption" color="primary.main" display="block" textAlign="right" mt={0.5} fontWeight={600}>
                      + Agregar a caja
                    </Typography>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </CardContent>
        </Card>

        <Dialog open={cartDialog} onClose={() => { if (!adding) { setCartDialog(false); setSelectedProduct(null) }}}
          maxWidth="xs" fullWidth PaperProps={{ sx: { borderRadius: 4 } }}>
          <DialogTitle sx={{ pb: 0 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="h6" fontWeight={700}>Agregar a caja</Typography>
              <IconButton size="small" onClick={() => { setCartDialog(false); setSelectedProduct(null) }}><Close /></IconButton>
            </Box>
            <Typography variant="body2" color="text.secondary" mt={0.5}>
              {selectedProduct?.nombre} — {formatMoney(selectedProduct?.precio)}
            </Typography>
          </DialogTitle>
          <DialogContent sx={{ pt: 2 }}>
            <Grid container spacing={1}>
              {[1, 2, 3, 4, 5, 6, 7, 8].map(n => (
                <Grid item xs={3} key={n}>
                  <Button fullWidth variant="outlined" disabled={adding}
                    onClick={() => addToCart(n)}
                    sx={{ borderRadius: 2, py: 1.5, fontWeight: 700, fontSize: '1rem' }}>
                    {n}
                  </Button>
                </Grid>
              ))}
            </Grid>
          </DialogContent>
        </Dialog>
      </Box>
    </Fade>
  )
}
