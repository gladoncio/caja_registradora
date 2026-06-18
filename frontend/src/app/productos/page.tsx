'use client'
import { useState, useEffect, useCallback, useMemo } from 'react'
import {
  Box, Card, CardContent, Grid, TextField, Button, Typography, IconButton,
  Chip, CircularProgress, Fade, alpha, Dialog, DialogTitle, DialogContent,
  DialogActions, Select, MenuItem, FormControl, InputLabel, Paper, Tooltip,
  InputAdornment, Divider, TablePagination,
} from '@mui/material'
import {
  Add, Edit, Delete, Inventory, Search, Close, Save, Star, StarBorder,
  ArrowUpward, ArrowDownward,
} from '@mui/icons-material'
import api, { productosAPI, configAPI } from '@/lib/api'
import { Producto, Configuracion } from '@/types'
import { useTheme } from '@mui/material'
import { formatMoney, formatNumber } from '@/lib/format'

interface ProductForm {
  id_producto?: number; nombre: string; precio: string; valor_costo: string
  codigo_barras: string; tipo_venta: string; departamento: number | ''; marca: number | ''
}

interface Depto { id: number; nombre: string }
interface MarcaType { id: number; nombre: string }

type SortField = 'nombre' | 'precio' | 'id_producto' | 'valor_costo'
type SortDir = 'asc' | 'desc'

const PAGE_SIZES = [12, 24, 48, 96]

export default function ProductosPage() {
  const theme = useTheme()
  const [productos, setProductos] = useState<Producto[]>([])
  const [deptos, setDeptos] = useState<Depto[]>([])
  const [marcas, setMarcas] = useState<MarcaType[]>([])
  const [rapidos, setRapidos] = useState<number[]>([])
  const [config, setConfig] = useState<Configuracion | null>(null)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [filterDepto, setFilterDepto] = useState<number | ''>('')
  const [filterTipo, setFilterTipo] = useState<string>('')
  const [filterRapido, setFilterRapido] = useState(false)
  const [sortField, setSortField] = useState<SortField>('id_producto')
  const [sortDir, setSortDir] = useState<SortDir>('desc')
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(24)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState<ProductForm>({
    nombre: '', precio: '', valor_costo: '', codigo_barras: '',
    tipo_venta: 'unidad', departamento: '', marca: '',
  })
  const [saving, setSaving] = useState(false)
  const [margen, setMargen] = useState(30)

  const loadData = useCallback(async () => {
    setLoading(true)
    try {
      const [p, d, m, c] = await Promise.all([
        api.get('/productos/', { params: { page_size: 9999 } }),
        api.get('/departamentos/'),
        api.get('/marcas/'),
        configAPI.get(),
      ])
      setProductos(p.data.results || p.data)
      setDeptos(d.data.results || d.data)
      setMarcas(m.data.results || m.data)
      setConfig(c.data)
      const r = await productosAPI.rapidos()
      setRapidos((r.data.results || r.data).map((x: any) => x.producto.id_producto))
    } finally { setLoading(false) }
  }, [])

  useEffect(() => { loadData() }, [loadData])

  // Sugerir precio basado en costo + margen
  useEffect(() => {
    const costo = parseFloat(form.valor_costo)
    if (costo > 0 && margen > 0) {
      setForm(f => ({ ...f, precio: Math.ceil(costo * (1 + margen / 100) / 10) * 10 + '' }))
    }
  }, [form.valor_costo, margen])

  const toggleRapido = async (id: number) => {
    if (rapidos.includes(id)) {
      await productosAPI.eliminarRapido(id)
      setRapidos(prev => prev.filter(x => x !== id))
    } else {
      if (rapidos.length >= 10) {
        alert('Máximo 10 productos rápidos. Quita uno antes de agregar otro.')
        return
      }
      await productosAPI.agregarRapido(id)
      setRapidos(prev => [...prev, id])
    }
  }

  // Filter and sort
  const filtered = useMemo(() => {
    let items = [...productos]
    if (search) {
      const q = search.toLowerCase()
      items = items.filter(p => p.nombre.toLowerCase().includes(q) || (p.codigo_barras || '').includes(q))
    }
    if (filterDepto) items = items.filter(p => p.departamento === filterDepto)
    if (filterTipo) items = items.filter(p => p.tipo_venta === filterTipo)
    if (filterRapido) items = items.filter(p => rapidos.includes(p.id_producto))
    items.sort((a, b) => {
      const mul = sortDir === 'asc' ? 1 : -1
      if (sortField === 'nombre') return mul * a.nombre.localeCompare(b.nombre)
      if (sortField === 'precio') return mul * (parseFloat(a.precio) - parseFloat(b.precio))
      if (sortField === 'valor_costo') return mul * (parseFloat(a.valor_costo || '0') - parseFloat(b.valor_costo || '0'))
      return mul * ((a.id_producto || 0) - (b.id_producto || 0))
    })
    return items
  }, [productos, search, filterDepto, filterTipo, filterRapido, rapidos, sortField, sortDir])

  const paginated = useMemo(() => {
    const start = page * rowsPerPage
    return filtered.slice(start, start + rowsPerPage)
  }, [filtered, page, rowsPerPage])

  const toggleSort = (field: SortField) => {
    if (sortField === field) setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    else { setSortField(field); setSortDir('asc') }
    setPage(0)
  }

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return null
    return sortDir === 'asc' ? <ArrowUpward fontSize="small" /> : <ArrowDownward fontSize="small" />
  }

  useEffect(() => { setPage(0) }, [search, filterDepto, filterTipo, filterRapido])

  const handleSave = async () => {
    if (!form.nombre || !form.precio) return
    setSaving(true)
    try {
      const data: any = { nombre: form.nombre, precio: form.precio, valor_costo: form.valor_costo || '0',
        codigo_barras: form.codigo_barras || undefined, tipo_venta: form.tipo_venta,
        departamento: form.departamento || null, marca: form.marca || null }
      if (form.id_producto) await productosAPI.update(form.id_producto, data)
      else await productosAPI.create(data)
      setDialogOpen(false); resetForm(); loadData()
    } catch { alert('Error al guardar') }
    finally { setSaving(false) }
  }

  const handleEdit = (p: Producto) => {
    setForm({ id_producto: p.id_producto, nombre: p.nombre, precio: p.precio.toString(),
      valor_costo: p.valor_costo?.toString() || '', codigo_barras: p.codigo_barras || '',
      tipo_venta: p.tipo_venta, departamento: p.departamento || '', marca: p.marca || '' })
    setDialogOpen(true)
  }

  const resetForm = () => setForm({ nombre: '', precio: '', valor_costo: '', codigo_barras: '', tipo_venta: 'unidad', departamento: '', marca: '' })

  return (
    <Fade in timeout={300}>
      <Box>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3} flexWrap="wrap" gap={1}>
          <Box display="flex" alignItems="center" gap={1.5}>
            <Inventory color="primary" />
            <Box>
              <Typography variant="h4" fontWeight={700}>Productos</Typography>
              <Typography variant="caption" color="text.secondary">{filtered.length} de {productos.length} productos</Typography>
            </Box>
          </Box>
          <Button variant="contained" startIcon={<Add />} onClick={() => { resetForm(); setDialogOpen(true) }} sx={{ borderRadius: 2 }}>
            Nuevo Producto
          </Button>
        </Box>

        {/* Filters */}
        <Card sx={{ borderRadius: 3, mb: 2 }}>
          <CardContent sx={{ py: 1.5, px: 2.5 }}>
            <Grid container spacing={1.5} alignItems="center">
              <Grid item xs={12} sm={4} md={3}>
                <TextField fullWidth size="small" placeholder="Buscar nombre o código..." value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  InputProps={{ startAdornment: <Search sx={{ mr: 0.5, fontSize: 20, color: 'text.secondary' }} /> }}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
              </Grid>
              <Grid item xs={6} sm={2}>
                <FormControl fullWidth size="small">
                  <InputLabel>Departamento</InputLabel>
                  <Select value={filterDepto} label="Departamento" onChange={(e) => setFilterDepto(e.target.value as number)} sx={{ borderRadius: 2 }}>
                    <MenuItem value=""><em>Todos</em></MenuItem>
                    {deptos.map(d => <MenuItem key={d.id} value={d.id}>{d.nombre}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={6} sm={2}>
                <FormControl fullWidth size="small">
                  <InputLabel>Tipo</InputLabel>
                  <Select value={filterTipo} label="Tipo" onChange={(e) => setFilterTipo(e.target.value)} sx={{ borderRadius: 2 }}>
                    <MenuItem value=""><em>Todos</em></MenuItem>
                    <MenuItem value="unidad">Unidad</MenuItem>
                    <MenuItem value="gramaje">Gramaje</MenuItem>
                    <MenuItem value="valor">Valor</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={6} sm={2}>
                <Chip label={`⭐ Rápidos (${rapidos.length}/10)`} color={filterRapido ? 'warning' : 'default'}
                  clickable onClick={() => setFilterRapido(!filterRapido)}
                  variant={filterRapido ? 'filled' : 'outlined'} sx={{ borderRadius: 1, width: '100%', fontWeight: 600 }} />
              </Grid>
              <Grid item xs={6} sm={2}>
                <Box display="flex" gap={0.5} flexWrap="wrap">
                  {[{ f: 'nombre', l: 'Nombre' }, { f: 'precio', l: 'Precio' }, { f: 'valor_costo', l: 'Costo' }, { f: 'id_producto', l: 'Fecha' }].map(s => (
                    <Chip key={s.f} label={s.l} size="small" clickable color={sortField === s.f ? 'primary' : 'default'}
                      onClick={() => toggleSort(s.f as SortField)}
                      icon={sortField === s.f ? (sortDir === 'asc' ? <ArrowUpward /> : <ArrowDownward />) : undefined}
                      sx={{ borderRadius: 1 }} />
                  ))}
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Product Grid */}
        {loading ? (
          <Box textAlign="center" py={6}><CircularProgress /></Box>
        ) : paginated.length === 0 ? (
          <Box textAlign="center" py={6}><Typography color="text.secondary">Sin resultados</Typography></Box>
        ) : (
          <>
            <Grid container spacing={1.5}>
              {paginated.map((p) => (
                <Grid item xs={6} sm={4} md={3} lg={2} key={p.id_producto}>
                  <Card sx={{ borderRadius: 2.5, position: 'relative', transition: 'all 0.15s ease',
                    '&:hover': { transform: 'translateY(-2px)', boxShadow: 4 } }}>
                    <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                      {/* Quick toggle */}
                      <IconButton size="small" onClick={() => toggleRapido(p.id_producto)}
                        sx={{ position: 'absolute', top: 2, right: 2, opacity: 0.7 }}>
                        {rapidos.includes(p.id_producto)
                          ? <Star sx={{ color: theme.palette.warning.main, fontSize: 18 }} />
                          : <StarBorder sx={{ fontSize: 18 }} />}
                      </IconButton>
                      <Typography variant="body2" fontWeight={700} noWrap pr={3}>{p.nombre}</Typography>
                      <Box display="flex" justifyContent="space-between" alignItems="center" mt={0.5}>
                        <Typography variant="h6" fontWeight={800} color="primary.main" sx={{ fontSize: '1rem' }}>
                          {formatMoney(p.precio)}
                        </Typography>
                        <Chip label={p.tipo_venta} size="small" variant="outlined" sx={{ height: 18, fontSize: 9 }} />
                      </Box>
                      {p.departamento_nombre && <Chip label={p.departamento_nombre} size="small" sx={{ height: 18, fontSize: 9, mt: 0.5 }} />}
                      <Box display="flex" gap={0.3} mt={0.5} justifyContent="flex-end">
                        <IconButton size="small" onClick={() => handleEdit(p)} sx={{ width: 24, height: 24 }}><Edit sx={{ fontSize: 14 }} /></IconButton>
                        <IconButton size="small" color="error" onClick={async () => { if (confirm('Eliminar?')) { await productosAPI.delete(p.id_producto); loadData() } }} sx={{ width: 24, height: 24 }}><Delete sx={{ fontSize: 14 }} /></IconButton>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
            <Box display="flex" justifyContent="center" mt={3}>
              <TablePagination component="div" count={filtered.length} page={page}
                onPageChange={(_, p) => setPage(p)} rowsPerPage={rowsPerPage}
                onRowsPerPageChange={(e) => { setRowsPerPage(parseInt(e.target.value, 10)); setPage(0) }}
                rowsPerPageOptions={PAGE_SIZES} />
            </Box>
          </>
        )}

        {/* Product Dialog */}
        <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { borderRadius: 4 } }}>
          <DialogTitle sx={{ pb: 0 }}><Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h6" fontWeight={700}>{form.id_producto ? 'Editar' : 'Nuevo'} Producto</Typography>
            <IconButton onClick={() => setDialogOpen(false)}><Close /></IconButton>
          </Box></DialogTitle>
          <DialogContent sx={{ pt: 3 }}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField fullWidth label="Nombre" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} autoFocus />
              </Grid>
              <Grid item xs={6}>
                <TextField fullWidth label="Código barras" value={form.codigo_barras} onChange={(e) => setForm({ ...form, codigo_barras: e.target.value })}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
              </Grid>
              <Grid item xs={6}>
                <FormControl fullWidth>
                  <InputLabel>Tipo venta</InputLabel>
                  <Select value={form.tipo_venta} label="Tipo venta" onChange={(e) => setForm({ ...form, tipo_venta: e.target.value })} sx={{ borderRadius: 2 }}>
                    <MenuItem value="unidad">Unidad</MenuItem><MenuItem value="gramaje">Gramaje</MenuItem><MenuItem value="valor">Valor</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}><Divider /></Grid>
              <Grid item xs={4}>
                <TextField fullWidth label="Costo" type="number" value={form.valor_costo}
                  onChange={(e) => setForm({ ...form, valor_costo: e.target.value })}
                  InputProps={{ startAdornment: <InputAdornment position="start">$</InputAdornment> }}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
              </Grid>
              <Grid item xs={4}>
                <TextField fullWidth label="Margen %" type="number" value={margen} onChange={(e) => setMargen(parseInt(e.target.value) || 0)}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
              </Grid>
              <Grid item xs={4}>
                <TextField fullWidth label="Precio venta" type="number" value={form.precio}
                  onChange={(e) => setForm({ ...form, precio: e.target.value })}
                  InputProps={{ startAdornment: <InputAdornment position="start">$</InputAdornment> }}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
              </Grid>
              <Grid item xs={6}>
                <FormControl fullWidth><InputLabel>Departamento</InputLabel>
                  <Select value={form.departamento} label="Departamento" onChange={(e) => setForm({ ...form, departamento: e.target.value as number })} sx={{ borderRadius: 2 }}>
                    <MenuItem value=""><em>Sin depto</em></MenuItem>
                    {deptos.map(d => <MenuItem key={d.id} value={d.id}>{d.nombre}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={6}>
                <FormControl fullWidth><InputLabel>Marca</InputLabel>
                  <Select value={form.marca} label="Marca" onChange={(e) => setForm({ ...form, marca: e.target.value as number })} sx={{ borderRadius: 2 }}>
                    <MenuItem value=""><em>Sin marca</em></MenuItem>
                    {marcas.map(m => <MenuItem key={m.id} value={m.id}>{m.nombre}</MenuItem>)}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions sx={{ p: 3, pt: 0, gap: 1 }}>
            <Button onClick={() => setDialogOpen(false)} variant="outlined" sx={{ borderRadius: 2 }}>Cancelar</Button>
            <Button onClick={handleSave} variant="contained" disabled={saving || !form.nombre || !form.precio}
              startIcon={saving ? <CircularProgress size={18} /> : <Save />} sx={{ borderRadius: 2 }}>
              {saving ? 'Guardando...' : form.id_producto ? 'Actualizar' : 'Crear'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Fade>
  )
}
