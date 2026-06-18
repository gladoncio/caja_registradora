'use client'
import { useState, useEffect, useMemo } from 'react'
import {
  Box, Card, CardContent, Typography, TextField, Chip, Fade, alpha, CircularProgress,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Grid,
  FormControl, InputLabel, Select, MenuItem,
} from '@mui/material'
import { History, Receipt, LocalAtm, CalendarMonth, Search } from '@mui/icons-material'
import api from '@/lib/api'
import { useTheme } from '@mui/material'
import { formatMoney, formatNumber } from '@/lib/format'

type EventType = 'venta' | 'gasto' | 'cierre'

interface LogEntry {
  id: string
  type: EventType
  fecha: string
  descripcion: string
  monto: number
  usuario?: string
}

export default function LogsPage() {
  const theme = useTheme()
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [filterType, setFilterType] = useState<string>('')
  const [filterDate, setFilterDate] = useState('')
  const [search, setSearch] = useState('')

  useEffect(() => {
    Promise.all([
      api.get('/ventas/', { params: { page_size: 100 } }).then(r => r.data.results || r.data).catch(() => []),
      api.get('/gastos/').then(r => r.data.results || r.data).catch(() => []),
      api.get('/reportes/cierres/').then(r => r.data || []).catch(() => []),
    ]).then(([ventas, gastos, cierres]) => {
      const entries: LogEntry[] = [
        ...ventas.map((v: any) => ({
          id: `v-${v.id}`, type: 'venta' as EventType,
          fecha: v.fecha_hora, descripcion: `Venta #${v.id}`,
          monto: parseFloat(v.total) || 0, usuario: v.usuario_username,
        })),
        ...gastos.map((g: any) => ({
          id: `g-${g.id}`, type: 'gasto' as EventType,
          fecha: g.fecha_hora, descripcion: g.descripcion || 'Gasto',
          monto: -(parseFloat(g.monto) || 0), usuario: g.usuario_username,
        })),
        ...cierres.map((c: any) => ({
          id: `c-${c.id}`, type: 'cierre' as EventType,
          fecha: c.fecha_ingreso, descripcion: `Cierre #${c.id}`,
          monto: c.monto_total || 0,
        })),
      ]
      entries.sort((a, b) => new Date(b.fecha).getTime() - new Date(a.fecha).getTime())
      setLogs(entries)
    }).finally(() => setLoading(false))
  }, [])

  const filtered = useMemo(() => {
    let items = [...logs]
    if (filterType) items = items.filter(l => l.type === filterType)
    if (filterDate) items = items.filter(l => l.fecha.startsWith(filterDate))
    if (search) {
      const q = search.toLowerCase()
      items = items.filter(l => l.descripcion.toLowerCase().includes(q))
    }
    return items
  }, [logs, filterType, filterDate, search])

  const typeColors: Record<string, 'success' | 'error' | 'info'> = { venta: 'success', gasto: 'error', cierre: 'info' }
  const typeIcons: Record<string, any> = { venta: <Receipt />, gasto: <LocalAtm />, cierre: <CalendarMonth /> }

  return (
    <Fade in timeout={300}>
      <Box>
        <Box display="flex" alignItems="center" gap={1.5} mb={3}>
          <History color="primary" />
          <Typography variant="h4" fontWeight={700}>Registro de Eventos</Typography>
        </Box>

        <Card sx={{ borderRadius: 3, mb: 2 }}>
          <CardContent sx={{ py: 1.5, px: 2.5 }}>
            <Grid container spacing={1.5} alignItems="center">
              <Grid item xs={12} sm={4}>
                <TextField fullWidth size="small" placeholder="Buscar..." value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  InputProps={{ startAdornment: <Search sx={{ mr: 0.5, fontSize: 20, color: 'text.secondary' }} /> }}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
              </Grid>
              <Grid item xs={6} sm={3}>
                <FormControl fullWidth size="small">
                  <InputLabel>Tipo</InputLabel>
                  <Select value={filterType} label="Tipo" onChange={(e) => setFilterType(e.target.value)} sx={{ borderRadius: 2 }}>
                    <MenuItem value="">Todos</MenuItem>
                    <MenuItem value="venta">Ventas</MenuItem>
                    <MenuItem value="gasto">Gastos</MenuItem>
                    <MenuItem value="cierre">Cierres</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={6} sm={3}>
                <TextField fullWidth size="small" type="date" value={filterDate}
                  onChange={(e) => setFilterDate(e.target.value)} label="Fecha"
                  InputLabelProps={{ shrink: true }} sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
              </Grid>
              <Grid item xs={12} sm={2}>
                <Chip label={`${filtered.length} eventos`} variant="outlined" sx={{ width: '100%', fontWeight: 600 }} />
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        <Card sx={{ borderRadius: 3 }}>
          <CardContent>
            {loading ? (
              <Box textAlign="center" py={4}><CircularProgress /></Box>
            ) : filtered.length === 0 ? (
              <Typography textAlign="center" py={4} color="text.secondary">Sin eventos</Typography>
            ) : (
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell width={80}>Tipo</TableCell>
                      <TableCell>Descripción</TableCell>
                      <TableCell width={180}>Fecha</TableCell>
                      <TableCell align="right" width={120}>Monto</TableCell>
                      <TableCell width={120}>Usuario</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {filtered.map(l => (
                      <TableRow key={l.id} hover>
                        <TableCell>
                          <Chip icon={typeIcons[l.type] as any} label={l.type} size="small"
                            color={typeColors[l.type]} sx={{ borderRadius: 1, fontWeight: 600 }} />
                        </TableCell>
                        <TableCell><Typography fontWeight={600}>{l.descripcion}</Typography></TableCell>
                        <TableCell>{new Date(l.fecha).toLocaleString('es-CL')}</TableCell>
                        <TableCell align="right">
                          <Typography fontWeight={700} color={l.monto < 0 ? 'error.main' : 'success.main'}>
                            {formatMoney(Math.abs(l.monto))}
                          </Typography>
                        </TableCell>
                        <TableCell>{l.usuario || '—'}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </CardContent>
        </Card>
      </Box>
    </Fade>
  )
}
