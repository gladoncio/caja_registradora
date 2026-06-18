'use client'
import { useState, useEffect } from 'react'
import {
  Box, Card, CardContent, Typography, Grid, TextField, Button, Chip,
  CircularProgress, Fade, Paper, alpha, Dialog, DialogTitle, DialogContent,
  DialogActions, IconButton, Switch, FormControlLabel, Tooltip,
} from '@mui/material'
import { Money, Add, Edit, Close, Save, Delete, CreditCard } from '@mui/icons-material'
import api from '@/lib/api'

const ICONOS = ['Money', 'CreditCard', 'SwapHoriz', 'AccountBalance', 'Payment', 'QrCode', 'PhoneIphone', 'Star']

export default function MetodosPagoPage() {
  const [metodos, setMetodos] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [dialog, setDialog] = useState(false)
  const [editing, setEditing] = useState<any>(null)
  const [form, setForm] = useState({ codigo: '', nombre: '', icono: 'Money', activo: true, orden: 0, requiere_autorizacion: false, color: '#6366f1', abre_gaveta: false, pide_monto: true, es_efectivo: false, da_vuelto: false, acepta_diferencia: true })

  const loadData = async () => {
    try { const r = await api.get('/metodos-pago/admin/'); setMetodos(r.data) }
    catch { } finally { setLoading(false) }
  }

  useEffect(() => { loadData() }, [])

  const handleSave = async () => {
    try {
      if (editing) await api.put(`/metodos-pago/${editing.id}/`, form)
      else await api.post('/metodos-pago/admin/', form)
      setDialog(false); setEditing(null); loadData()
    } catch { }
  }

  const handleDelete = async (id: number) => {
    try { await api.delete(`/metodos-pago/${id}/`); loadData() }
    catch { }
  }

  if (loading) return <Box display="flex" justifyContent="center" py={6}><CircularProgress /></Box>

  return (
    <Fade in timeout={300}>
      <Box>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3} flexWrap="wrap" gap={1}>
          <Box display="flex" alignItems="center" gap={1.5}>
            <CreditCard color="primary" />
            <Box>
              <Typography variant="h4" fontWeight={700}>Métodos de Pago</Typography>
              <Typography variant="caption" color="text.secondary">{metodos.length} método(s)</Typography>
            </Box>
          </Box>
          <Button variant="contained" startIcon={<Add />}
            onClick={() => { setEditing(null); setForm({ codigo: '', nombre: '', icono: 'Money', activo: true, orden: 0, requiere_autorizacion: false, color: '#6366f1', abre_gaveta: false, pide_monto: true, es_efectivo: false, da_vuelto: false, acepta_diferencia: true }); setDialog(true) }}
            sx={{ borderRadius: 2 }}>
            Nuevo Método
          </Button>
        </Box>

        <Grid container spacing={2}>
          {metodos.map((m) => (
            <Grid item xs={12} sm={6} md={4} key={m.id}>
              <Card sx={{ borderRadius: 3, opacity: m.activo ? 1 : 0.5 }}>
                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                  <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                    <Box display="flex" alignItems="center" gap={1.5}>
                      <Box sx={{ width: 40, height: 40, borderRadius: 2, bgcolor: m.color, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <CreditCard sx={{ color: '#fff', fontSize: 20 }} />
                      </Box>
                      <Box>
                        <Typography fontWeight={700}>{m.nombre}</Typography>
                        <Typography variant="caption" color="text.secondary">{m.codigo}</Typography>
                      </Box>
                    </Box>
                    <Box display="flex" gap={0.3}>
                      <IconButton size="small" onClick={() => { setEditing(m); setForm({ codigo: m.codigo, nombre: m.nombre, icono: m.icono, activo: m.activo, orden: m.orden, requiere_autorizacion: m.requiere_autorizacion, color: m.color, abre_gaveta: m.abre_gaveta, pide_monto: m.pide_monto, es_efectivo: m.es_efectivo, da_vuelto: m.da_vuelto, acepta_diferencia: m.acepta_diferencia }); setDialog(true) }}>
                        <Edit fontSize="small" />
                      </IconButton>
                      <IconButton size="small" color="error" onClick={() => handleDelete(m.id)}>
                        <Delete fontSize="small" />
                      </IconButton>
                    </Box>
                  </Box>
                  <Box mt={1} display="flex" gap={0.5} flexWrap="wrap">
                    <Chip label={`Orden ${m.orden}`} size="small" variant="outlined" sx={{ height: 18, fontSize: 9 }} />
                    {!m.activo && <Chip label="Inactivo" size="small" color="warning" sx={{ height: 18, fontSize: 9 }} />}
                    {m.requiere_autorizacion && <Chip label="Requiere auth" size="small" color="error" sx={{ height: 18, fontSize: 9 }} />}
                    {m.abre_gaveta && <Chip label="Gaveta" size="small" color="info" sx={{ height: 18, fontSize: 9 }} />}
                    {m.pide_monto && <Chip label="Pide monto" size="small" sx={{ height: 18, fontSize: 9 }} />}
                    {m.es_efectivo && <Chip label="Efectivo" size="small" color="success" sx={{ height: 18, fontSize: 9 }} />}
                    {m.da_vuelto && <Chip label="Da vuelto" size="small" color="secondary" sx={{ height: 18, fontSize: 9 }} />}
                    {m.acepta_diferencia && <Chip label="Acepta resto" size="small" variant="outlined" color="primary" sx={{ height: 18, fontSize: 9 }} />}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        <Dialog open={dialog} onClose={() => setDialog(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { borderRadius: 4 } }}>
          <DialogTitle sx={{ pb: 0 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="h6" fontWeight={700}>{editing ? 'Editar' : 'Nuevo'} Método de Pago</Typography>
              <IconButton onClick={() => setDialog(false)}><Close /></IconButton>
            </Box>
          </DialogTitle>
          <DialogContent sx={{ pt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField fullWidth label="Código interno" value={form.codigo} onChange={(e) => setForm({ ...form, codigo: e.target.value })}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
              </Grid>
              <Grid item xs={6}>
                <TextField fullWidth label="Nombre visible" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
              </Grid>
              <Grid item xs={4}>
                <TextField fullWidth label="Orden" type="number" value={form.orden}
                  onChange={(e) => setForm({ ...form, orden: parseInt(e.target.value) || 0 })}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
              </Grid>
              <Grid item xs={4}>
                <Box>
                  <Typography variant="caption" color="text.secondary">Color</Typography>
                  <input type="color" value={form.color}
                    onChange={(e) => setForm({ ...form, color: e.target.value })}
                    style={{ width: '100%', height: 40, border: 'none', borderRadius: 8, cursor: 'pointer', padding: 0 }} />
                </Box>
              </Grid>
              <Grid item xs={4}>
                <TextField fullWidth label="Icono" value={form.icono}
                  onChange={(e) => setForm({ ...form, icono: e.target.value })}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel control={<Switch checked={form.activo} onChange={(e) => setForm({ ...form, activo: e.target.checked })} />} label="Activo" />
                <FormControlLabel control={<Switch checked={form.requiere_autorizacion} onChange={(e) => setForm({ ...form, requiere_autorizacion: e.target.checked })} />} label="Requiere autorización" />
              </Grid>
              <Grid item xs={12}>
                <FormControlLabel control={<Switch checked={form.abre_gaveta} onChange={(e) => setForm({ ...form, abre_gaveta: e.target.checked })} />} label="Abre la gaveta" />
                <FormControlLabel control={<Switch checked={form.pide_monto} onChange={(e) => setForm({ ...form, pide_monto: e.target.checked })} />} label="Pide monto al usuario" />
                <FormControlLabel control={<Switch checked={form.es_efectivo} onChange={(e) => setForm({ ...form, es_efectivo: e.target.checked })} />} label="Es efectivo (da vuelto)" />
                <FormControlLabel control={<Switch checked={form.da_vuelto} onChange={(e) => setForm({ ...form, da_vuelto: e.target.checked })} />} label="Puede dar vuelto" />
                <FormControlLabel control={<Switch checked={form.acepta_diferencia} onChange={(e) => setForm({ ...form, acepta_diferencia: e.target.checked })} />} label="Acepta pago de diferencia (resto)" />
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
      </Box>
    </Fade>
  )
}
