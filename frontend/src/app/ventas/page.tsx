'use client'
import { useState, useEffect, useCallback } from 'react'
import {
  Box, Card, CardContent, Typography, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Chip, CircularProgress, TextField, Grid,
  Button, Fade, alpha, IconButton, Tooltip, Paper,
} from '@mui/material'
import { Receipt, Delete, ReceiptLong, Info } from '@mui/icons-material'
import { ventasAPI } from '@/lib/api'
import { Venta } from '@/types'

export default function VentasPage() {
  const [ventas, setVentas] = useState<Venta[]>([])
  const [loading, setLoading] = useState(true)
  const [fecha, setFecha] = useState('')
  const [horaInicio, setHoraInicio] = useState('')
  const [horaFin, setHoraFin] = useState('')
  const [selectedVenta, setSelectedVenta] = useState<Venta | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const params: any = {}
      if (fecha) params.fecha = fecha
      if (horaInicio) params.hora_inicio = horaInicio
      if (horaFin) params.hora_fin = horaFin
      const r = await ventasAPI.list(params)
      setVentas(r.data.results || r.data)
    } finally { setLoading(false) }
  }, [fecha, horaInicio, horaFin])

  useEffect(() => { load() }, [load])

  const handleEliminar = async (id: number) => {
    const clave = prompt('Ingresa tu clave de anulación:')
    if (clave) { try { await ventasAPI.eliminar(id, clave); load() } catch { alert('Error') } }
  }

  const formatDate = (d: string) => new Date(d).toLocaleString('es-CL')

  return (
    <Fade in timeout={400}>
      <Box>
        <Box display="flex" alignItems="center" gap={1} mb={3}>
          <ReceiptLong color="primary" />
          <Typography variant="h4" fontWeight={700}>Ventas</Typography>
        </Box>

        <Card sx={{ mb: 2, borderRadius: 3 }}>
          <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
            <Grid container spacing={2} alignItems="end">
              <Grid item xs={12} sm={4}>
                <TextField fullWidth size="small" label="Fecha" type="date" value={fecha}
                  onChange={(e) => setFecha(e.target.value)} InputLabelProps={{ shrink: true }}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
              </Grid>
              <Grid item xs={6} sm={3}>
                <TextField fullWidth size="small" label="Desde" type="time" value={horaInicio}
                  onChange={(e) => setHoraInicio(e.target.value)} InputLabelProps={{ shrink: true }}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
              </Grid>
              <Grid item xs={6} sm={3}>
                <TextField fullWidth size="small" label="Hasta" type="time" value={horaFin}
                  onChange={(e) => setHoraFin(e.target.value)} InputLabelProps={{ shrink: true }}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
              </Grid>
              <Grid item xs={12} sm={2}>
                <Button fullWidth variant="contained" onClick={load} sx={{ borderRadius: 2 }}>Filtrar</Button>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        <Card sx={{ borderRadius: 3 }}>
          <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
            {loading ? (
              <Box display="flex" justifyContent="center" py={6}><CircularProgress /></Box>
            ) : ventas.length === 0 ? (
              <Box textAlign="center" py={6}>
                <ReceiptLong sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
                <Typography color="text.secondary">No hay ventas en este período</Typography>
              </Box>
            ) : (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>#</TableCell>
                      <TableCell>Fecha</TableCell>
                      <TableCell>Usuario</TableCell>
                      <TableCell align="right">Total</TableCell>
                      <TableCell>Pago</TableCell>
                      <TableCell align="right">Acción</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {ventas.map((v) => (
                      <TableRow key={v.id} hover>
                        <TableCell><Typography fontWeight={700}>#{v.id}</Typography></TableCell>
                        <TableCell>{formatDate(v.fecha_hora)}</TableCell>
                        <TableCell>{v.usuario_username}</TableCell>
                        <TableCell align="right">
                          <Typography fontWeight={700} color="primary.main">
                            ${parseInt(v.total).toLocaleString('es-CL')}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Box display="flex" gap={0.5}>
                            {v.formas_pago.map((fp) => (
                              <Chip key={fp.tipo_pago} label={fp.tipo_pago} size="small"
                                color={fp.tipo_pago === 'efectivo' ? 'success' : 'info'}
                                sx={{ borderRadius: 1 }} />
                            ))}
                          </Box>
                        </TableCell>
                        <TableCell align="right">
                          <Tooltip title="Ver detalle">
                            <IconButton size="small" onClick={() => setSelectedVenta(v)}>
                              <Info fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Anular venta">
                            <IconButton size="small" color="error" onClick={() => handleEliminar(v.id)}>
                              <Delete fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </CardContent>
        </Card>

        {/* Venta Detail Dialog */}
        {selectedVenta && (
          <Box
            sx={{
              position: 'fixed', right: 0, top: 64, bottom: 0, width: { xs: '100%', sm: 400 },
              bgcolor: 'background.paper', zIndex: 1200, boxShadow: -4,
              borderLeft: 1, borderColor: 'divider', p: 3, overflow: 'auto',
            }}
          >
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6" fontWeight={700}>Venta #{selectedVenta.id}</Typography>
              <IconButton onClick={() => setSelectedVenta(null)}><Delete /></IconButton>
            </Box>
            <Typography variant="body2" color="text.secondary" mb={2}>{formatDate(selectedVenta.fecha_hora)}</Typography>
            <Divider sx={{ mb: 2 }} />
            {selectedVenta.productos.map((vp, i) => (
              <Box key={i} display="flex" justifyContent="space-between" mb={1}>
                <Typography variant="body2">{vp.producto_nombre} × {vp.cantidad || `${vp.gramaje}g`}</Typography>
                <Typography variant="body2" fontWeight={600}>${parseInt(vp.subtotal).toLocaleString('es-CL')}</Typography>
              </Box>
            ))}
            <Divider sx={{ my: 2 }} />
            <Box display="flex" justifyContent="space-between">
              <Typography fontWeight={700}>Total</Typography>
              <Typography fontWeight={800} color="primary.main">${parseInt(selectedVenta.total).toLocaleString('es-CL')}</Typography>
            </Box>
          </Box>
        )}
      </Box>
    </Fade>
  )
}

const Divider = ({ sx }: any) => <Box sx={{ height: 1, bgcolor: 'divider', my: 1, ...sx }} />
