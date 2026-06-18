'use client'
import { useState, useEffect, useMemo, useCallback } from 'react'
import {
  Box, Card, CardContent, Typography, Grid, Paper, Chip, alpha, Fade, IconButton,
  TextField, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  CircularProgress, Alert,
} from '@mui/material'
import { CalendarMonth, Search, ChevronLeft, ChevronRight } from '@mui/icons-material'
import api, { reportesAPI } from '@/lib/api'
import { formatMoney, formatNumber } from '@/lib/format'
import { useTheme } from '@mui/material'

export default function CalendarioPage() {
  const theme = useTheme()
  const [cierres, setCierres] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<any>(null)
  const [date, setDate] = useState(new Date())
  const [filterDate, setFilterDate] = useState('')
  const [viewMode, setViewMode] = useState<'calendar' | 'list'>('calendar')
  const [printing, setPrinting] = useState(false)
  const [msg, setMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  useEffect(() => {
    api.get('/reportes/cierres/').then((r) => setCierres(r.data || [])).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const { year, month, firstDay, daysInMonth, getCierre } = useMemo(() => {
    const y = date.getFullYear()
    const m = date.getMonth()
    const fd = new Date(y, m, 1).getDay()
    const dim = new Date(y, m + 1, 0).getDate()
    const map: Record<string, any> = {}
    cierres.forEach(c => {
      const d = new Date(c.fecha_ingreso)
      const key = `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`
      if (!map[key] || new Date(c.fecha_ingreso) > new Date(map[key].fecha_ingreso)) map[key] = c
    })
    const gc = (day: number) => map[`${y}-${m}-${day}`]
    return { year: y, month: m, firstDay: fd, daysInMonth: dim, getCierre: gc }
  }, [date, cierres])

  const filteredCierres = useMemo(() => {
    if (!filterDate) return cierres
    return cierres.filter((c: any) => c.fecha_ingreso.startsWith(filterDate))
  }, [cierres, filterDate])

  const today = new Date()
  const monthName = date.toLocaleDateString('es-CL', { month: 'long', year: 'numeric' })

  useEffect(() => { setMsg(null) }, [selected])

  const handleNavigate = useCallback((delta: number) => {
    setDate(prev => new Date(prev.getFullYear(), prev.getMonth() + delta, 1))
  }, [])

  const handlePrint = useCallback(async () => {
    if (!selected || printing) return
    setPrinting(true)
    try {
      await reportesAPI.imprimirCierre(selected.id)
      setMsg({ type: 'success', text: 'Reporte enviado a la impresora' })
    } catch {
      setMsg({ type: 'error', text: 'Error al imprimir' })
    } finally {
      setPrinting(false)
    }
  }, [selected, printing])

  if (loading) return <Box display="flex" justifyContent="center" py={6}><CircularProgress /></Box>

  return (
    <Fade in timeout={300}>
      <Box>
        <Box display="flex" alignItems="center" gap={1.5} mb={3} flexWrap="wrap" justifyContent="space-between">
          <Box display="flex" alignItems="center" gap={1.5}>
            <CalendarMonth color="primary" />
            <Box>
              <Typography variant="h4" fontWeight={700}>Calendario de Cierres</Typography>
              <Typography variant="caption" color="text.secondary">{cierres.length} cierre(s)</Typography>
            </Box>
          </Box>
          <Box display="flex" gap={1}>
            <Button variant={viewMode === 'calendar' ? 'contained' : 'outlined'} size="small"
              onClick={() => setViewMode('calendar')} sx={{ borderRadius: 2 }}>Calendario</Button>
            <Button variant={viewMode === 'list' ? 'contained' : 'outlined'} size="small"
              onClick={() => setViewMode('list')} sx={{ borderRadius: 2 }}>Lista</Button>
          </Box>
        </Box>

        <Card sx={{ borderRadius: 3, mb: 2 }}>
          <CardContent sx={{ py: 1.5, px: 2.5, display: 'flex', alignItems: 'center', gap: 2, flexWrap: 'wrap' }}>
            <Search sx={{ color: 'text.secondary' }} />
            <TextField size="small" type="date" value={filterDate} onChange={(e) => setFilterDate(e.target.value)}
              sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 }, width: 200 }} label="Filtrar" InputLabelProps={{ shrink: true }} />
            {filterDate && <Button size="small" onClick={() => { setFilterDate(''); setSelected(null) }} sx={{ borderRadius: 2 }}>Limpiar</Button>}
            <Chip label={`${filteredCierres.length} resultado(s)`} size="small" variant="outlined" />
          </CardContent>
        </Card>

        {viewMode === 'calendar' ? (
          <Grid container spacing={2}>
            <Grid item xs={12} md={7}>
              <Card sx={{ borderRadius: 3 }}>
                <CardContent sx={{ p: { xs: 1.5, sm: 2, md: 3 } }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <IconButton onClick={() => handleNavigate(-1)} size="small"><ChevronLeft /></IconButton>
                    <Typography variant="h5" fontWeight={700} sx={{ textTransform: 'capitalize' }}>{monthName}</Typography>
                    <IconButton onClick={() => handleNavigate(1)} size="small"><ChevronRight /></IconButton>
                  </Box>
                  <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', borderTop: 1, borderLeft: 1, borderColor: 'divider' }}>
                    {['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'].map(d => (
                      <Typography key={d} variant="caption" color="text.secondary" align="center" fontWeight={700}
                        sx={{ py: 0.5, borderRight: 1, borderBottom: 1, borderColor: 'divider', bgcolor: alpha(theme.palette.grey[500], 0.04) }}>{d}</Typography>
                    ))}
                    {Array.from({ length: firstDay }).map((_, i) => (
                      <Box key={`e-${i}`} sx={{ borderRight: 1, borderBottom: 1, borderColor: 'divider' }} />
                    ))}
                    {Array.from({ length: daysInMonth }).map((_, i) => {
                      const day = i + 1
                      const isToday = day === today.getDate() && month === today.getMonth() && year === today.getFullYear()
                      const cierre = getCierre(day)
                      const isSel = selected && new Date(selected.fecha_ingreso).getDate() === day && new Date(selected.fecha_ingreso).getMonth() === month && new Date(selected.fecha_ingreso).getFullYear() === year
                      return (
                        <Box key={day} onClick={() => cierre ? setSelected(isSel ? null : cierre) : setSelected(null)}
                          sx={{
                            aspectRatio: '1',
                            cursor: cierre ? 'pointer' : 'default',
                            bgcolor: isSel ? alpha(theme.palette.primary.main, 0.12)
                              : isToday ? alpha(theme.palette.primary.main, 0.05)
                              : undefined,
                            borderRight: 1, borderBottom: 1, borderColor: 'divider',
                            transition: 'all 0.12s',
                            display: 'flex', flexDirection: 'column', p: 0.3,
                            '&:hover': cierre ? { bgcolor: alpha(theme.palette.primary.main, 0.08) } : {},
                          }}>
                          <Box sx={{
                            width: 22, height: 22, display: 'flex', alignItems: 'center', justifyContent: 'center',
                            borderRadius: '50%',
                            bgcolor: isToday ? 'primary.main' : undefined,
                            mb: 0.3,
                          }}>
                            <Typography sx={{
                              fontSize: { xs: '0.75rem', sm: '0.8rem' },
                              fontWeight: isToday ? 700 : 500,
                              color: isToday ? '#fff' : (cierre ? 'text.primary' : 'text.disabled'),
                              lineHeight: 1,
                            }}>
                              {day}
                            </Typography>
                          </Box>
                          {cierre && (
                            <Typography sx={{
                              fontSize: { xs: '0.5rem', sm: '0.55rem' },
                              fontWeight: 700, color: 'success.dark', lineHeight: 1.1,
                              mt: 'auto', mb: 0.3, textAlign: 'center',
                            }}>
                              {formatMoney(cierre.monto_total)}
                            </Typography>
                          )}
                        </Box>
                      )
                    })}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={5}>
              <Card sx={{ borderRadius: 3, position: 'sticky', top: 80 }}>
                <CardContent sx={{ p: 2.5 }}>
                  {selected ? (
                    <>
                      <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1.5}>
                        <Box>
                          <Typography variant="h6" fontWeight={700}>Cierre del día</Typography>
                          <Typography variant="body2" color="text.secondary" sx={{ textTransform: 'capitalize' }}>
                            {new Date(selected.fecha_ingreso).toLocaleDateString('es-CL', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                          </Typography>
                        </Box>
                        <Button variant="contained" size="small" disabled={printing} onClick={handlePrint}
                          sx={{ borderRadius: 2, minWidth: 0, px: 1.5, py: 0.5, fontSize: '0.75rem' }}>
                          {printing ? 'Imprimiendo...' : 'Imprimir'}
                        </Button>
                      </Box>
                      <Typography variant="caption" color="text.disabled" display="block" mb={2}>Hora: {new Date(selected.fecha_ingreso).toLocaleTimeString('es-CL')} · ID #{selected.id}</Typography>

                      <Paper elevation={0} sx={{ background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.08)}, ${alpha(theme.palette.primary.dark, 0.04)})`, p: 2, borderRadius: 2, textAlign: 'center', mb: 2, border: 2, borderColor: alpha(theme.palette.primary.main, 0.1) }}>
                        <Typography variant="caption" color="text.secondary">Total Neto General</Typography>
                        <Typography variant="h4" fontWeight={800} color="primary.main">{formatMoney(selected.monto_total)}</Typography>
                      </Paper>

                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.8 }}>
                        {[
                          { label: 'Efectivo', value: selected.monto_efectivo, color: 'success' },
                          { label: 'Débito', value: selected.monto_debito, color: 'info' },
                          { label: 'Transferencia', value: selected.monto_transferencia, color: 'warning' },
                          { label: 'Retiro', value: selected.monto_retiro, color: 'error' },
                          { label: 'Caja Diaria', value: selected.valor_caja_diaria, color: 'secondary' },
                        ].map(s => (
                          <Box key={s.label} sx={{
                            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                            bgcolor: alpha((theme.palette as any)[s.color]?.main || theme.palette.grey[500], 0.04),
                            borderRadius: 1.5, px: 1.5, py: 0.8,
                          }}>
                            <Typography variant="body2" fontWeight={500} color="text.secondary">{s.label}</Typography>
                            <Typography variant="body2" fontWeight={700}
                              sx={{ color: (theme.palette as any)[s.color]?.main || 'text.primary' }}>
                              {formatMoney(s.value)}
                            </Typography>
                          </Box>
                        ))}
                      </Box>
                      {msg && (
                        <Alert severity={msg.type} sx={{ mt: 2, borderRadius: 2 }}
                          onClose={() => setMsg(null)}>
                          {msg.text}
                        </Alert>
                      )}
                    </>
                  ) : (
                    <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" py={4} gap={1}>
                      <CalendarMonth sx={{ fontSize: 48, color: alpha(theme.palette.grey[500], 0.3) }} />
                      <Typography variant="body2" color="text.disabled" textAlign="center">
                        Selecciona un día<br />con cierre para ver el detalle
                      </Typography>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        ) : (
          <Card sx={{ borderRadius: 3 }}>
            <CardContent>
              {filteredCierres.length === 0 ? (
                <Typography textAlign="center" py={4} color="text.secondary">No hay cierres registrados</Typography>
              ) : (
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Fecha</TableCell>
                        <TableCell align="right">Total</TableCell>
                        <TableCell align="right">Efectivo</TableCell>
                        <TableCell align="right">Débito</TableCell>
                        <TableCell align="right">Transferencia</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {filteredCierres.map((c: any) => (
                        <TableRow key={c.id} hover sx={{ cursor: 'pointer' }} onClick={() => setSelected(selected?.id === c.id ? null : c)}>
                          <TableCell>{new Date(c.fecha_ingreso).toLocaleDateString('es-CL', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</TableCell>
                          <TableCell align="right"><Typography fontWeight={700}>{formatMoney(c.monto_total)}</Typography></TableCell>
                          <TableCell align="right">{formatMoney(c.monto_efectivo)}</TableCell>
                          <TableCell align="right">{formatMoney(c.monto_debito)}</TableCell>
                          <TableCell align="right">{formatMoney(c.monto_transferencia)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>
        )}
      </Box>
    </Fade>
  )
}
