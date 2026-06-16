'use client'
import { useState, useEffect } from 'react'
import {
  Box, Card, CardContent, Grid, Typography, Button, TextField, Fade,
  CircularProgress, Paper, alpha, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Chip, Divider, IconButton, Tooltip,
} from '@mui/material'
import { Assessment, Check, SyncAlt } from '@mui/icons-material'
import { reportesAPI } from '@/lib/api'
import { useTheme } from '@mui/material'

type Modo = 'cantidad' | 'subtotal'

interface Denominacion {
  campo: string
  label: string
  tipo: string
  valor: number
  modo: Modo
  cantidad: number
  subtotal: number
}

const DENOMINACIONES: Denominacion[] = [
  { campo: 'monedas_10', label: '$10', tipo: 'Moneda', valor: 10, modo: 'cantidad', cantidad: 0, subtotal: 0 },
  { campo: 'monedas_50', label: '$50', tipo: 'Moneda', valor: 50, modo: 'cantidad', cantidad: 0, subtotal: 0 },
  { campo: 'monedas_100', label: '$100', tipo: 'Moneda', valor: 100, modo: 'cantidad', cantidad: 0, subtotal: 0 },
  { campo: 'monedas_500', label: '$500', tipo: 'Moneda', valor: 500, modo: 'cantidad', cantidad: 0, subtotal: 0 },
  { campo: 'billetes_1000', label: '$1.000', tipo: 'Billete', valor: 1000, modo: 'cantidad', cantidad: 0, subtotal: 0 },
  { campo: 'billetes_2000', label: '$2.000', tipo: 'Billete', valor: 2000, modo: 'cantidad', cantidad: 0, subtotal: 0 },
  { campo: 'billetes_5000', label: '$5.000', tipo: 'Billete', valor: 5000, modo: 'cantidad', cantidad: 0, subtotal: 0 },
  { campo: 'billetes_10000', label: '$10.000', tipo: 'Billete', valor: 10000, modo: 'cantidad', cantidad: 0, subtotal: 0 },
  { campo: 'billetes_20000', label: '$20.000', tipo: 'Billete', valor: 20000, modo: 'cantidad', cantidad: 0, subtotal: 0 },
]

export default function CuadrePage() {
  const theme = useTheme()
  const [loading, setLoading] = useState(true)
  const [resultado, setResultado] = useState<any>(null)
  const [rows, setRows] = useState<Denominacion[]>(DENOMINACIONES)
  const [maquinasDebito, setMaquinasDebito] = useState('')
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => { setLoading(false) }, [])

  const totalEfectivo = rows.reduce((s, r) => s + (r.cantidad * r.valor), 0)

  const handleCantidadChange = (campo: string, val: string) => {
    setRows(prev => prev.map(r => {
      if (r.campo !== campo) return r
      const cant = parseInt(val) || 0
      return { ...r, cantidad: cant, subtotal: cant * r.valor, modo: 'cantidad' }
    }))
  }

  const handleSubtotalChange = (campo: string, val: string) => {
    setRows(prev => prev.map(r => {
      if (r.campo !== campo) return r
      const sub = parseInt(val) || 0
      return { ...r, subtotal: sub, cantidad: r.valor > 0 ? Math.round(sub / r.valor) : 0, modo: 'subtotal' }
    }))
  }

  const handleSubmit = async () => {
    setSubmitting(true)
    try {
      const data: any = { maquinas_debito: parseInt(maquinasDebito) || 0 }
      rows.forEach(r => { data[r.campo] = r.cantidad })
      const res = await reportesAPI.cuadrar(data)
      setResultado(res.data)
    } catch { alert('Error al procesar cuadre') }
    finally { setSubmitting(false) }
  }

  if (loading) return <Box display="flex" justifyContent="center" py={6}><CircularProgress /></Box>

  return (
    <Fade in timeout={300}>
      <Box>
        <Box display="flex" alignItems="center" gap={1.5} mb={3}>
          <Box sx={{ width: 40, height: 40, borderRadius: 2, display: 'flex', alignItems: 'center', justifyContent: 'center',
            background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`, color: '#fff' }}>
            <Assessment fontSize="small" />
          </Box>
          <Typography variant="h4" fontWeight={700}>Cuadre de Caja</Typography>
        </Box>

        {!resultado ? (
          <Card sx={{ borderRadius: 3 }}>
            <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
              <Typography variant="h6" fontWeight={700} mb={2}>Conteo de Dinero</Typography>
              <Typography variant="caption" color="text.secondary" display="block" mb={2}>
                Ingresa la <strong>cantidad</strong> o el <strong>subtotal</strong> de cada denominación
              </Typography>

              {/* Desktop table */}
              <TableContainer sx={{ display: { xs: 'none', sm: 'block' }, borderRadius: 2, border: 1, borderColor: 'divider' }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Tipo</TableCell>
                      <TableCell>Denominación</TableCell>
                      <TableCell align="center" width={140}>Cantidad</TableCell>
                      <TableCell align="right" width={160}>Subtotal</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {rows.map((r) => (
                      <TableRow key={r.campo} hover>
                        <TableCell><Chip label={r.tipo} size="small" variant="outlined" sx={{ minWidth: 60 }} /></TableCell>
                        <TableCell><Typography fontWeight={600}>{r.label}</Typography></TableCell>
                        <TableCell align="center" width={140}>
                          <TextField size="small" type="number" value={r.cantidad || ''}
                            onChange={(e) => handleCantidadChange(r.campo, e.target.value)}
                            inputProps={{ min: 0, style: { textAlign: 'center' } }}
                            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 }, width: 100 }} />
                        </TableCell>
                        <TableCell align="right" width={160}>
                          <TextField size="small" type="number" value={r.subtotal || ''}
                            onChange={(e) => handleSubtotalChange(r.campo, e.target.value)}
                            InputProps={{ startAdornment: <Typography variant="caption" sx={{ mr: 0.5, color: 'text.secondary' }}>$</Typography> }}
                            inputProps={{ style: { textAlign: 'right' } }}
                            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 }, width: 130 }} />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>

              {/* Mobile cards */}
              <Box sx={{ display: { xs: 'block', sm: 'none' } }}>
                {rows.map((r) => (
                  <Paper key={r.campo} elevation={0} sx={{ p: 1.5, mb: 1, borderRadius: 2, border: 1, borderColor: 'divider' }}>
                    <Box display="flex" justifyContent="space-between" mb={1}>
                      <Chip label={r.tipo} size="small" variant="outlined" />
                      <Typography fontWeight={700}>{r.label}</Typography>
                      <Typography fontWeight={700} color="primary.main">${r.subtotal.toLocaleString('es-CL')}</Typography>
                    </Box>
                    <Box display="flex" gap={1}>
                      <TextField size="small" label="Cantidad" type="number" value={r.cantidad || ''}
                        onChange={(e) => handleCantidadChange(r.campo, e.target.value)}
                        sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 }, flex: 1 }} />
                      <TextField size="small" label="Subtotal $" type="number" value={r.subtotal || ''}
                        onChange={(e) => handleSubtotalChange(r.campo, e.target.value)}
                        sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 }, flex: 1 }} />
                    </Box>
                  </Paper>
                ))}
              </Box>

              <Box display="flex" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={2} mt={3}>
                <TextField label="Monto máquinas débito" type="number" value={maquinasDebito}
                  onChange={(e) => setMaquinasDebito(e.target.value)}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 }, width: { xs: '100%', sm: 260 } }} />
                <Box textAlign="right">
                  <Typography variant="caption" color="text.secondary">Total efectivo contado</Typography>
                  <Typography variant="h4" fontWeight={800} color="primary.main">
                    ${totalEfectivo.toLocaleString('es-CL')}
                  </Typography>
                </Box>
              </Box>

              <Button fullWidth variant="contained" size="large" onClick={handleSubmit} disabled={submitting}
                startIcon={submitting ? <CircularProgress size={20} color="inherit" /> : <Check />}
                sx={{ mt: 3, py: 1.5, borderRadius: 3, fontWeight: 700 }}>
                {submitting ? 'Procesando...' : 'Realizar Cuadre'}
              </Button>
            </CardContent>
          </Card>
        ) : (
          <Card sx={{ borderRadius: 3 }}>
            <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
              <Typography variant="h5" fontWeight={700} mb={3}>Resultado del Cuadre</Typography>
              <Grid container spacing={2}>
                <Grid item xs={6} sm={3}>
                  <Paper elevation={0} sx={{ p: 2, borderRadius: 2, bgcolor: alpha(theme.palette.info.main, 0.05), textAlign: 'center' }}>
                    <Typography variant="caption" color="text.secondary">Esperado</Typography>
                    <Typography variant="h6" fontWeight={700}>${(resultado.total_efectivo_esperado || 0).toLocaleString('es-CL')}</Typography>
                  </Paper>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Paper elevation={0} sx={{ p: 2, borderRadius: 2, bgcolor: alpha(theme.palette.success.main, 0.05), textAlign: 'center' }}>
                    <Typography variant="caption" color="text.secondary">Contado</Typography>
                    <Typography variant="h6" fontWeight={700}>${(resultado.total_efectivo_contado || 0).toLocaleString('es-CL')}</Typography>
                  </Paper>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Paper elevation={0} sx={{ p: 2, borderRadius: 2, textAlign: 'center',
                    bgcolor: (resultado.diferencia_efectivo || 0) < 0 ? alpha(theme.palette.success.main, 0.1) : alpha(theme.palette.error.main, 0.1) }}>
                    <Typography variant="caption" color="text.secondary">Diferencia efectivo</Typography>
                    <Typography variant="h6" fontWeight={700}
                      color={(resultado.diferencia_efectivo || 0) < 0 ? 'success.main' : 'error.main'}>
                      {resultado.estado_efectivo === 'sobrante' ? '+' : ''}${Math.abs(resultado.diferencia_efectivo || 0).toLocaleString('es-CL')}
                    </Typography>
                    <Chip label={resultado.estado_efectivo} size="small"
                      color={(resultado.diferencia_efectivo || 0) < 0 ? 'success' : 'error'} sx={{ mt: 0.5 }} />
                  </Paper>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Paper elevation={0} sx={{ p: 2, borderRadius: 2, bgcolor: alpha(theme.palette.warning.main, 0.05), textAlign: 'center' }}>
                    <Typography variant="caption" color="text.secondary">Diferencia débito</Typography>
                    <Typography variant="h6" fontWeight={700}>${(resultado.diferencia_debito || 0).toLocaleString('es-CL')}</Typography>
                  </Paper>
                </Grid>
              </Grid>
              <Box display="flex" justifyContent="flex-end" mt={3} gap={1}>
                <Button variant="outlined" onClick={() => setResultado(null)} sx={{ borderRadius: 2 }}>Nuevo cuadre</Button>
                <Button variant="contained" onClick={() => setResultado(null)} sx={{ borderRadius: 2 }}>Cerrar</Button>
              </Box>
            </CardContent>
          </Card>
        )}
      </Box>
    </Fade>
  )
}
