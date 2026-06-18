'use client'
import { useState, useEffect } from 'react'
import {
  Box, Card, CardContent, Grid, Typography, CircularProgress, Divider,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
  Button, TextField, Dialog, DialogTitle, DialogContent, DialogActions, Fade,
  alpha, Chip, IconButton, Tooltip,
} from '@mui/material'
import { Assessment, Add, AttachMoney, Money, CreditCard, Receipt, LocalAtm } from '@mui/icons-material'
import { reportesAPI, gastosAPI } from '@/lib/api'
import { InformeGeneral, Gasto } from '@/types'
import { formatMoney, formatNumber } from '@/lib/format'

export default function ReportesPage() {
  const [reporte, setReporte] = useState<InformeGeneral | null>(null)
  const [gastos, setGastos] = useState<Gasto[]>([])
  const [loading, setLoading] = useState(true)
  const [gastoDialog, setGastoDialog] = useState(false)
  const [gastoMonto, setGastoMonto] = useState('')
  const [gastoDesc, setGastoDesc] = useState('')

  const loadData = async () => {
    setLoading(true)
    try {
      const [r, g] = await Promise.all([reportesAPI.general(), gastosAPI.list()])
      setReporte(r.data)
      setGastos(g.data.results || g.data)
    } finally { setLoading(false) }
  }

  useEffect(() => { loadData() }, [])

  if (loading) return <Box display="flex" justifyContent="center" py={6}><CircularProgress /></Box>
  if (!reporte) return <Typography>Error cargando reporte</Typography>

  const stats = [
    { label: 'Total Ventas', value: formatMoney(reporte.total_ventas), color: 'primary.main', icon: <Receipt /> },
    { label: 'Efectivo', value: formatMoney(reporte.monto_efectivo), color: 'success.main', icon: <Money /> },
    { label: 'Débito', value: formatMoney(reporte.monto_debito), color: 'info.main', icon: <CreditCard /> },
    { label: 'Transferencia', value: formatMoney(reporte.monto_transferencia), color: 'warning.main', icon: <AttachMoney /> },
    { label: 'Gastos', value: `-${formatMoney(reporte.total_gastos)}`, color: 'error.main', icon: <LocalAtm /> },
    { label: 'Caja debería tener', value: formatMoney(reporte.caja_que_deberia), color: 'secondary.main', icon: <Assessment /> },
  ]

  return (
    <Fade in timeout={400}>
      <Box>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Box display="flex" alignItems="center" gap={1}>
            <Assessment color="primary" />
            <Typography variant="h4" fontWeight={700}>Reporte General</Typography>
          </Box>
          <Button variant="contained" startIcon={<Add />} onClick={() => setGastoDialog(true)} sx={{ borderRadius: 2 }}>
            Registrar Gasto
          </Button>
        </Box>

        <Grid container spacing={2} mb={3}>
          {stats.map((s) => (
            <Grid item xs={6} sm={4} md={2} key={s.label}>
              <Card sx={{ borderRadius: 3, textAlign: 'center' }}>
                <CardContent sx={{ py: 2 }}>
                  <Box sx={{ color: s.color, mb: 1 }}>{s.icon}</Box>
                  <Typography variant="caption" color="text.secondary" display="block">{s.label}</Typography>
                  <Typography variant="h6" fontWeight={800} sx={{ color: s.color }}>
                    {s.value}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Card sx={{ borderRadius: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom fontWeight={700}>Ventas por Departamento</Typography>
                {reporte.ventas_por_departamento.length === 0 ? (
                  <Typography color="text.secondary" variant="body2">Sin datos</Typography>
                ) : (
                  reporte.ventas_por_departamento.map((vd) => (
                    <Box key={vd.producto__departamento__nombre} display="flex" justifyContent="space-between" py={0.5}>
                      <Typography variant="body2">{vd.producto__departamento__nombre || 'Sin departamento'}</Typography>
                      <Typography variant="body2" fontWeight={700}>
                        {formatMoney(vd.total)}
                      </Typography>
                    </Box>
                  ))
                )}
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card sx={{ borderRadius: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom fontWeight={700}>Gastos del Período</Typography>
                {gastos.length === 0 ? (
                  <Typography color="text.secondary" variant="body2" textAlign="center" py={3}>Sin gastos registrados</Typography>
                ) : (
                  <TableContainer>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Descripción</TableCell>
                          <TableCell align="right">Monto</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {gastos.map((g) => (
                          <TableRow key={g.id}>
                            <TableCell>
                              <Typography variant="body2">{g.descripcion}</Typography>
                              <Typography variant="caption" color="text.secondary">{new Date(g.fecha_hora).toLocaleString('es-CL')}</Typography>
                            </TableCell>
                            <TableCell align="right">
                              <Typography fontWeight={700} color="error.main">
                                -{formatMoney(g.monto)}
                              </Typography>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Dialog open={gastoDialog} onClose={() => setGastoDialog(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { borderRadius: 4 } }}>
          <DialogTitle fontWeight={700}>Registrar Gasto</DialogTitle>
          <DialogContent>
            <TextField fullWidth label="Monto" type="number" margin="normal" value={gastoMonto}
              onChange={(e) => setGastoMonto(e.target.value)}
              sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
            <TextField fullWidth label="Descripción" margin="normal" multiline rows={2} value={gastoDesc}
              onChange={(e) => setGastoDesc(e.target.value)}
              sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
          </DialogContent>
          <DialogActions sx={{ p: 3, pt: 0 }}>
            <Button onClick={() => setGastoDialog(false)} sx={{ borderRadius: 2 }}>Cancelar</Button>
            <Button variant="contained" onClick={async () => {
              await gastosAPI.create({ monto: gastoMonto, descripcion: gastoDesc })
              setGastoDialog(false); setGastoMonto(''); setGastoDesc(''); loadData()
            }} sx={{ borderRadius: 2 }}>Guardar</Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Fade>
  )
}
