'use client'
import { useState, useEffect, useMemo, useCallback } from 'react'
import {
  Box, Card, CardContent, Typography, Grid, Paper, Chip, alpha, Fade, IconButton,
  TextField, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  CircularProgress,
} from '@mui/material'
import { CalendarMonth, Search, ChevronLeft, ChevronRight } from '@mui/icons-material'
import api from '@/lib/api'
import { useTheme } from '@mui/material'

const STAT_COLORS = ['primary', 'success', 'info', 'secondary'] as const

export default function CalendarioPage() {
  const theme = useTheme()
  const [cierres, setCierres] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<any>(null)
  const [date, setDate] = useState(new Date())
  const [filterDate, setFilterDate] = useState('')
  const [viewMode, setViewMode] = useState<'calendar' | 'list'>('calendar')

  useEffect(() => {
    api.get('/reportes/cierres/').then((r) => setCierres(r.data || [])).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const { year, month, firstDay, daysInMonth, cierreMap, getCierre } = useMemo(() => {
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
    return { year: y, month: m, firstDay: fd, daysInMonth: dim, cierreMap: map, getCierre: gc }
  }, [date, cierres])

  const filteredCierres = useMemo(() => {
    if (!filterDate) return cierres
    return cierres.filter((c: any) => c.fecha_ingreso.startsWith(filterDate))
  }, [cierres, filterDate])

  const today = new Date()
  const monthName = date.toLocaleDateString('es-CL', { month: 'long', year: 'numeric' })

  const monthlyTotals = useMemo(() => {
    const totals = { total: 0, efectivo: 0, debito: 0, count: 0 }
    Object.values(cierreMap).forEach(c => {
      const d = new Date(c.fecha_ingreso)
      if (d.getMonth() === month && d.getFullYear() === year) {
        totals.total += c.monto_total || 0
        totals.efectivo += c.monto_efectivo || 0
        totals.debito += c.monto_debito || 0
        totals.count++
      }
    })
    return totals
  }, [cierreMap, month, year])

  const monthlyStats = [
    { label: 'Total', value: monthlyTotals.total, colorKey: 'primary' },
    { label: 'Efectivo', value: monthlyTotals.efectivo, colorKey: 'success' },
    { label: 'Débito', value: monthlyTotals.debito, colorKey: 'info' },
    { label: 'Cierres', value: monthlyTotals.count, colorKey: 'secondary' as string, isCount: true },
  ]

  const handleNavigate = useCallback((delta: number) => {
    setDate(prev => new Date(prev.getFullYear(), prev.getMonth() + delta, 1))
  }, [])

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
            <Grid item xs={12} md={selected ? 7 : 12}>
              <Card sx={{ borderRadius: 3 }}>
                <CardContent sx={{ p: { xs: 1.5, sm: 2, md: 3 } }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <IconButton onClick={() => handleNavigate(-1)} size="small"><ChevronLeft /></IconButton>
                    <Typography variant="h5" fontWeight={700} sx={{ textTransform: 'capitalize' }}>{monthName}</Typography>
                    <IconButton onClick={() => handleNavigate(1)} size="small"><ChevronRight /></IconButton>
                  </Box>
                  <Grid container spacing={0.5} mb={1}>
                    {['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'].map(d => (
                      <Grid item xs key={d}><Typography variant="caption" color="text.secondary" align="center" display="block" fontWeight={700}>{d}</Typography></Grid>
                    ))}
                  </Grid>
                  <Grid container spacing={0.5}>
                    {Array.from({ length: firstDay }).map((_, i) => (
                      <Grid item xs key={`e-${i}`}><Box sx={{ width: '100%', pt: '80%' }} /></Grid>
                    ))}
                    {Array.from({ length: daysInMonth }).map((_, i) => {
                      const day = i + 1
                      const isToday = day === today.getDate() && month === today.getMonth() && year === today.getFullYear()
                      const cierre = getCierre(day)
                      const isSel = selected && new Date(selected.fecha_ingreso).getDate() === day && new Date(selected.fecha_ingreso).getMonth() === month && new Date(selected.fecha_ingreso).getFullYear() === year
                      return (
                        <Grid item xs key={day}>
                          <Box onClick={() => cierre ? setSelected(isSel ? null : cierre) : setSelected(null)}
                            sx={{ width: '100%', pt: '80%', position: 'relative', cursor: cierre ? 'pointer' : 'default', borderRadius: 2,
                              bgcolor: isSel ? alpha(theme.palette.primary.main, 0.18) : cierre ? alpha(theme.palette.success.main, 0.1) : 'transparent',
                              border: isToday ? 2 : 0, borderColor: 'primary.main', transition: 'all 0.15s ease',
                              '&:hover': cierre ? { bgcolor: alpha(theme.palette.primary.main, 0.1) } : {} }}>
                            <Box sx={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', p: 0.3 }}>
                              <Typography variant="body2" fontWeight={isToday || !!cierre ? 700 : 400} lineHeight={1}>{day}</Typography>
                              {cierre && <Chip label={`$${(cierre.monto_total || 0).toLocaleString('es-CL')}`} size="small"
                                sx={{ height: 18, fontSize: 9, mt: 0.3, bgcolor: isSel ? 'primary.main' : alpha(theme.palette.success.main, 0.15), color: isSel ? '#fff' : 'success.main', fontWeight: 700, maxWidth: '95%' }} />}
                            </Box>
                          </Box>
                        </Grid>
                      )
                    })}
                  </Grid>
                  {monthlyTotals.count > 0 && (
                    <Box mt={2} pt={2} borderTop={1} borderColor="divider">
                      <Typography variant="subtitle2" fontWeight={700} mb={1}>Resumen del mes</Typography>
                      <Grid container spacing={1}>
                        {monthlyStats.map((s, idx) => {
                          const paletteKey = s.colorKey as 'primary' | 'success' | 'info' | 'secondary'
                          const colorStr = theme.palette[paletteKey].main
                          return (
                            <Grid item xs={3} key={s.label}>
                              <Paper elevation={0} sx={{ p: 1, borderRadius: 2, bgcolor: alpha(colorStr, 0.06), textAlign: 'center' }}>
                                <Typography variant="caption" color="text.secondary">{s.label}</Typography>
                                <Typography variant="body2" fontWeight={700} sx={{ color: colorStr }}>
                                  {s.isCount ? s.value : `$${s.value.toLocaleString('es-CL')}`}
                                </Typography>
                              </Paper>
                            </Grid>
                          )
                        })}
                      </Grid>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
            {selected && (
              <Grid item xs={12} md={5}>
                <Card sx={{ borderRadius: 3, position: 'sticky', top: 80 }}>
                  <CardContent sx={{ p: 3 }}>
                    <Typography variant="h6" fontWeight={700} mb={0.5}>Cierre del día</Typography>
                    <Typography variant="body2" color="text.secondary" mb={2} sx={{ textTransform: 'capitalize' }}>
                      {new Date(selected.fecha_ingreso).toLocaleDateString('es-CL', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                    </Typography>
                    <Typography variant="caption" color="text.disabled" display="block" mb={2}>Hora: {new Date(selected.fecha_ingreso).toLocaleTimeString('es-CL')} · ID #{selected.id}</Typography>
                    <Paper elevation={0} sx={{ background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.08)}, ${alpha(theme.palette.primary.dark, 0.04)})`, p: 2.5, borderRadius: 3, textAlign: 'center', mb: 2, border: 2, borderColor: alpha(theme.palette.primary.main, 0.1) }}>
                      <Typography variant="caption" color="text.secondary">Total del período</Typography>
                      <Typography variant="h3" fontWeight={800} color="primary.main">${(selected.monto_total || 0).toLocaleString('es-CL')}</Typography>
                    </Paper>
                    <Grid container spacing={1}>
                      {[
                        { label: 'Efectivo', value: selected.monto_efectivo, color: 'success' },
                        { label: 'Débito', value: selected.monto_debito, color: 'info' },
                        { label: 'Transferencia', value: selected.monto_transferencia, color: 'warning' },
                      ].map(s => {
                        const colorVal = (theme.palette as any)[s.color]?.main || theme.palette.primary.main
                        return (
                          <Grid item xs={4} key={s.label}>
                            <Paper elevation={0} sx={{ p: 1.5, borderRadius: 2, bgcolor: alpha(colorVal, 0.05), textAlign: 'center' }}>
                              <Typography variant="caption" color="text.secondary">{s.label}</Typography>
                              <Typography variant="body1" fontWeight={700} sx={{ color: colorVal }}>${(s.value || 0).toLocaleString('es-CL')}</Typography>
                            </Paper>
                          </Grid>
                        )
                      })}
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
            )}
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
                          <TableCell align="right"><Typography fontWeight={700}>${(c.monto_total || 0).toLocaleString('es-CL')}</Typography></TableCell>
                          <TableCell align="right">${(c.monto_efectivo || 0).toLocaleString('es-CL')}</TableCell>
                          <TableCell align="right">${(c.monto_debito || 0).toLocaleString('es-CL')}</TableCell>
                          <TableCell align="right">${(c.monto_transferencia || 0).toLocaleString('es-CL')}</TableCell>
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
