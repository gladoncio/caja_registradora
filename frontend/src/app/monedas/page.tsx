'use client'
import { useState, useEffect } from 'react'
import {
  Box, Card, CardContent, Typography, Grid, TextField, Button, Chip,
  CircularProgress, Fade, Paper, alpha, Dialog, DialogTitle, DialogContent,
  DialogActions, IconButton, Switch, FormControlLabel, Select, MenuItem,
  FormControl, InputLabel,
} from '@mui/material'
import { Money, Add, Edit, Close, Save, Delete, SwapHoriz } from '@mui/icons-material'
import api from '@/lib/api'
import { formatMoney } from '@/lib/format'

interface Moneda {
  id: number
  codigo: string
  nombre: string
  simbolo: string
  decimales: number
  separador_miles: string
  separador_decimal: string
  locale: string
  activa: boolean
  orden: number
}

interface TasaCambio {
  id: number
  moneda_origen: number
  moneda_destino: number
  moneda_origen_codigo: string
  moneda_destino_codigo: string
  tasa: string
}

const LOCALES = ['es-CL', 'en-US', 'de-DE', 'es-AR', 'pt-BR', 'fr-FR', 'en-GB']

export default function MonedasPage() {
  const [monedas, setMonedas] = useState<Moneda[]>([])
  const [tasas, setTasas] = useState<TasaCambio[]>([])
  const [loading, setLoading] = useState(true)
  const [dialog, setDialog] = useState(false)
  const [tasaDialog, setTasaDialog] = useState(false)
  const [editing, setEditing] = useState<Moneda | null>(null)
  const [form, setForm] = useState({
    codigo: '', nombre: '', simbolo: '$', decimales: 0,
    separador_miles: '.', separador_decimal: ',', locale: 'es-CL', activa: true, orden: 0,
  })
  const [tasaForm, setTasaForm] = useState({ moneda_origen: '', moneda_destino: '', tasa: '' })
  const [tasaCantidadOrigen, setTasaCantidadOrigen] = useState('1')
  const [tasaCantidadDestino, setTasaCantidadDestino] = useState('')

  const loadData = async () => {
    try {
      const [m, t] = await Promise.all([
        api.get('/monedas/'),
        api.get('/tasas-cambio/'),
      ])
      setMonedas(m.data)
      setTasas(t.data)
    } catch { } finally { setLoading(false) }
  }

  useEffect(() => { loadData() }, [])

  const handleSave = async () => {
    try {
      if (editing) {
        await api.put(`/monedas/${editing.id}/`, form)
      } else {
        await api.post('/monedas/', form)
      }
      setDialog(false)
      setEditing(null)
      loadData()
    } catch { }
  }

  const handleDelete = async (id: number) => {
    try {
      await api.delete(`/monedas/${id}/`)
      loadData()
    } catch { }
  }

  const handleTasaCalc = (lado: 'origen' | 'destino', val: string) => {
    if (lado === 'origen') {
      setTasaCantidadOrigen(val)
      const num = parseFloat(val)
      if (num > 0 && tasaForm.moneda_origen && tasaForm.moneda_destino) {
        const tasa = parseFloat(tasaForm.tasa)
        setTasaCantidadDestino(tasa && num ? (num * tasa).toString() : '')
      }
    } else {
      setTasaCantidadDestino(val)
      const num = parseFloat(val)
      if (num > 0 && tasaForm.moneda_origen && tasaForm.moneda_destino) {
        const tasa = parseFloat(tasaForm.tasa)
        setTasaCantidadOrigen(tasa && num ? (num / tasa).toString() : '')
      }
    }
  }

  const handleTasaMetaChange = (field: string, val: string) => {
    setTasaForm(f => ({ ...f, [field]: val }))
    if (field === 'tasa') {
      const num = parseFloat(val)
      if (num > 0 && tasaCantidadOrigen) {
        setTasaCantidadDestino((parseFloat(tasaCantidadOrigen) * num).toString())
      }
    }
    if (field === 'moneda_origen' || field === 'moneda_destino') {
      setTasaCantidadOrigen('1')
      setTasaCantidadDestino('')
    }
  }

  const handleSaveTasa = async () => {
    try {
      const origenId = parseInt(tasaForm.moneda_origen)
      const destinoId = parseInt(tasaForm.moneda_destino)
      const cOrigen = parseFloat(tasaCantidadOrigen) || 1
      const cDestino = parseFloat(tasaCantidadDestino) || 0
      const tasa = cDestino / cOrigen
      await api.post('/tasas-cambio/', {
        moneda_origen: origenId,
        moneda_destino: destinoId,
        tasa: tasa.toString(),
      })
      setTasaDialog(false)
      setTasaForm({ moneda_origen: '', moneda_destino: '', tasa: '' })
      setTasaCantidadOrigen('1')
      setTasaCantidadDestino('')
      loadData()
    } catch { }
  }

  if (loading) return <Box display="flex" justifyContent="center" py={6}><CircularProgress /></Box>

  return (
    <Fade in timeout={300}>
      <Box>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3} flexWrap="wrap" gap={1}>
          <Box display="flex" alignItems="center" gap={1.5}>
            <Money color="primary" />
            <Box>
              <Typography variant="h4" fontWeight={700}>Monedas</Typography>
              <Typography variant="caption" color="text.secondary">{monedas.length} moneda(s)</Typography>
            </Box>
          </Box>
          <Box display="flex" gap={1}>
            <Button variant="outlined" startIcon={<SwapHoriz />} onClick={() => setTasaDialog(true)} sx={{ borderRadius: 2 }}>
              Tasa de cambio
            </Button>
            <Button variant="contained" startIcon={<Add />} onClick={() => { setEditing(null); setForm({ codigo: '', nombre: '', simbolo: '$', decimales: 0, separador_miles: '.', separador_decimal: ',', locale: 'es-CL', activa: true, orden: 0 }); setDialog(true) }} sx={{ borderRadius: 2 }}>
              Nueva Moneda
            </Button>
          </Box>
        </Box>

        <Grid container spacing={2}>
          {monedas.map((m) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={m.id}>
              <Card sx={{ borderRadius: 3, opacity: m.activa ? 1 : 0.5 }}>
                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                    <Box>
                      <Box display="flex" alignItems="center" gap={0.5}>
                        <Typography variant="h5" fontWeight={800}>{m.simbolo}</Typography>
                        <Chip label={m.codigo} size="small" color="primary" sx={{ fontWeight: 700, height: 20 }} />
                      </Box>
                      <Typography variant="body2" fontWeight={600} mt={0.5}>{m.nombre}</Typography>
                    </Box>
                    <Box display="flex" gap={0.3}>
                      <IconButton size="small" onClick={() => { setEditing(m); setForm({ codigo: m.codigo, nombre: m.nombre, simbolo: m.simbolo, decimales: m.decimales, separador_miles: m.separador_miles, separador_decimal: m.separador_decimal, locale: m.locale, activa: m.activa, orden: m.orden }); setDialog(true) }}>
                        <Edit fontSize="small" />
                      </IconButton>
                      <IconButton size="small" color="error" onClick={() => handleDelete(m.id)}>
                        <Delete fontSize="small" />
                      </IconButton>
                    </Box>
                  </Box>
                  <Box mt={1} display="flex" gap={0.5} flexWrap="wrap">
                    <Chip label={`${m.decimales} decimales`} size="small" variant="outlined" sx={{ height: 18, fontSize: 9 }} />
                    <Chip label={m.locale} size="small" variant="outlined" sx={{ height: 18, fontSize: 9 }} />
                    {!m.activa && <Chip label="Inactiva" size="small" color="warning" sx={{ height: 18, fontSize: 9 }} />}
                  </Box>
                  <Box mt={1}>
                    <Typography variant="caption" color="text.secondary">
                      Sep. miles: "{m.separador_miles}" · Sep. decimal: "{m.separador_decimal}"
                    </Typography>
                  </Box>
                  <Box mt={0.5}>
                    <Typography variant="caption" color="text.secondary">
                      Preview: {formatMoney(1234567.89)}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        <Card sx={{ borderRadius: 3, mt: 3 }}>
          <CardContent sx={{ p: 3 }}>
            <Box display="flex" alignItems="center" gap={1} mb={2}>
              <SwapHoriz color="primary" />
              <Typography variant="h6" fontWeight={700}>Tasas de Cambio</Typography>
            </Box>
            {tasas.length === 0 ? (
              <Typography color="text.secondary" textAlign="center" py={2}>Sin tasas configuradas</Typography>
            ) : (
              <Grid container spacing={1}>
                {tasas.map((t) => {
                  const origen = monedas.find(m => m.id === t.moneda_origen)
                  const destino = monedas.find(m => m.id === t.moneda_destino)
                  return (
                    <Grid item xs={12} sm={6} md={4} key={t.id}>
                      <Paper elevation={0} sx={{ p: 1.5, borderRadius: 2, border: 1, borderColor: 'divider' }}>
                        <Typography fontWeight={600}>
                          1 {origen?.codigo || '?'} = {parseFloat(t.tasa).toFixed(6)} {destino?.codigo || '?'}
                        </Typography>
                      </Paper>
                    </Grid>
                  )
                })}
              </Grid>
            )}
          </CardContent>
        </Card>

        <Dialog open={dialog} onClose={() => setDialog(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { borderRadius: 4 } }}>
          <DialogTitle sx={{ pb: 0 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="h6" fontWeight={700}>{editing ? 'Editar' : 'Nueva'} Moneda</Typography>
              <IconButton onClick={() => setDialog(false)}><Close /></IconButton>
            </Box>
          </DialogTitle>
          <DialogContent sx={{ pt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField fullWidth label="Código" value={form.codigo} onChange={(e) => setForm({ ...form, codigo: e.target.value.toUpperCase() })}
                  inputProps={{ maxLength: 3 }} sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
              </Grid>
              <Grid item xs={6}>
                <TextField fullWidth label="Símbolo" value={form.simbolo} onChange={(e) => setForm({ ...form, simbolo: e.target.value })}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
              </Grid>
              <Grid item xs={12}>
                <TextField fullWidth label="Nombre" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
              </Grid>
              <Grid item xs={4}>
                <TextField fullWidth label="Decimales" type="number" value={form.decimales}
                  onChange={(e) => setForm({ ...form, decimales: parseInt(e.target.value) || 0 })}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
              </Grid>
              <Grid item xs={4}>
                <TextField fullWidth label="Sep. miles" value={form.separador_miles}
                  onChange={(e) => setForm({ ...form, separador_miles: e.target.value })}
                  inputProps={{ maxLength: 1 }} sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
              </Grid>
              <Grid item xs={4}>
                <TextField fullWidth label="Sep. decimal" value={form.separador_decimal}
                  onChange={(e) => setForm({ ...form, separador_decimal: e.target.value })}
                  inputProps={{ maxLength: 1 }} sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
              </Grid>
              <Grid item xs={6}>
                <FormControl fullWidth>
                  <InputLabel>Locale</InputLabel>
                  <Select value={form.locale} label="Locale" onChange={(e) => setForm({ ...form, locale: e.target.value })} sx={{ borderRadius: 2 }}>
                    {LOCALES.map(l => <MenuItem key={l} value={l}>{l}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={6}>
                <TextField fullWidth label="Orden" type="number" value={form.orden}
                  onChange={(e) => setForm({ ...form, orden: parseInt(e.target.value) || 0 })}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel control={<Switch checked={form.activa} onChange={(e) => setForm({ ...form, activa: e.target.checked })} />}
                  label="Activa" />
              </Grid>
              <Grid item xs={12}>
                <Paper elevation={0} sx={{ p: 1.5, borderRadius: 2, bgcolor: alpha('#6366f1', 0.04), textAlign: 'center' }}>
                  <Typography variant="body2" color="text.secondary">Preview</Typography>
                  <Typography variant="h5" fontWeight={800}>{form.simbolo}{new Intl.NumberFormat(form.locale, { minimumFractionDigits: form.decimales, maximumFractionDigits: form.decimales }).format(1234567.89)}</Typography>
                </Paper>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions sx={{ p: 3, pt: 0, gap: 1 }}>
            <Button onClick={() => setDialog(false)} variant="outlined" sx={{ borderRadius: 2 }}>Cancelar</Button>
            <Button onClick={handleSave} variant="contained" startIcon={<Save />} disabled={!form.codigo || !form.nombre} sx={{ borderRadius: 2 }}>
              {editing ? 'Actualizar' : 'Crear'}
            </Button>
          </DialogActions>
        </Dialog>

        <Dialog open={tasaDialog} onClose={() => setTasaDialog(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { borderRadius: 4 } }}>
          <DialogTitle sx={{ pb: 0 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="h6" fontWeight={700}>Nueva Tasa de Cambio</Typography>
              <IconButton onClick={() => setTasaDialog(false)}><Close /></IconButton>
            </Box>
          </DialogTitle>
          <DialogContent sx={{ pt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <FormControl fullWidth>
                  <InputLabel>Desde</InputLabel>
                  <Select value={tasaForm.moneda_origen} label="Desde" onChange={(e) => handleTasaMetaChange('moneda_origen', e.target.value)} sx={{ borderRadius: 2 }}>
                    {monedas.map(m => <MenuItem key={m.id} value={m.id}>{m.codigo}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={6}>
                <FormControl fullWidth>
                  <InputLabel>Hasta</InputLabel>
                  <Select value={tasaForm.moneda_destino} label="Hasta" onChange={(e) => handleTasaMetaChange('moneda_destino', e.target.value)} sx={{ borderRadius: 2 }}>
                    {monedas.map(m => <MenuItem key={m.id} value={m.id}>{m.codigo}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={5}>
                <TextField fullWidth label="Cantidad origen" type="number" value={tasaCantidadOrigen}
                  onChange={(e) => handleTasaCalc('origen', e.target.value)}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
              </Grid>
              <Grid item xs={2} display="flex" alignItems="center" justifyContent="center">
                <Typography variant="h5" fontWeight={700} color="text.disabled">=</Typography>
              </Grid>
              <Grid item xs={5}>
                <TextField fullWidth label="Cantidad destino" type="number" value={tasaCantidadDestino}
                  onChange={(e) => handleTasaCalc('destino', e.target.value)}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
              </Grid>
              <Grid item xs={12}>
                <Paper elevation={0} sx={{ p: 1.5, borderRadius: 2, bgcolor: (t) => alpha(t.palette.info.main, 0.05), textAlign: 'center' }}>
                  <Typography variant="caption" color="text.secondary">Tasa calculada</Typography>
                  <Typography fontWeight={700}>
                    {tasaCantidadOrigen && tasaCantidadDestino
                      ? `1 ${monedas.find(m => m.id === parseInt(tasaForm.moneda_origen))?.codigo || '?'} = ${(parseFloat(tasaCantidadDestino) / parseFloat(tasaCantidadOrigen)).toFixed(6)} ${monedas.find(m => m.id === parseInt(tasaForm.moneda_destino))?.codigo || '?'}`
                      : 'Ingresa cantidades para calcular'}
                  </Typography>
                </Paper>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions sx={{ p: 3, pt: 0 }}>
            <Button onClick={() => setTasaDialog(false)} variant="outlined" sx={{ borderRadius: 2 }}>Cancelar</Button>
            <Button onClick={handleSaveTasa} variant="contained" disabled={!tasaForm.moneda_origen || !tasaForm.moneda_destino || !tasaCantidadDestino} sx={{ borderRadius: 2 }}>
              Agregar
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Fade>
  )
}
