'use client'
import { useState, useEffect, useCallback, useRef, useMemo } from 'react'
import {
  Box, Card, CardContent, Grid, TextField, Button, Typography, IconButton,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Dialog, DialogTitle, DialogContent, DialogActions, Chip, Snackbar, Alert,
  CircularProgress, List, ListItemButton, ListItemText,
  Paper, InputAdornment, Zoom, Tooltip, Divider, alpha,
  Tabs, Tab, Menu, MenuItem, ListItemIcon, useTheme, useMediaQuery,
} from '@mui/material'
import {
  Add, Remove, Delete, Search, ShoppingCart, Payment, QrCodeScanner,
  Keyboard, PointOfSale, Close, Check, Money, Casino, CreditCard,
  Speed, Star, StarBorder, KeyboardAlt, SwapHoriz, AccountBalance,
} from '@mui/icons-material'
import { carritoAPI, productosAPI, ventasAPI, metodosPagoAPI, configAPI, impresoraAPI, autorizacionAPI } from '@/lib/api'
import { CarritoItem, ProductoSimple, ProductoRapido, Configuracion } from '@/types'
import { useKeyboardShortcuts } from '@/lib/shortcuts'
import AuthorizationDialog from '@/components/AuthorizationDialog'
import BigAlert from '@/components/BigAlert'
import { formatMoney, formatNumber, redondear } from '@/lib/format'

function getIcon(name: string) {
  const icons: Record<string, React.ReactNode> = {
    Money: <Money />, CreditCard: <CreditCard />, SwapHoriz: <SwapHoriz />,
    AccountBalance: <AccountBalance />, Payment: <Payment />, QrCode: <QrCodeScanner />,
  }
  return icons[name] || <Money />
}

interface PagoState {
  metodo: string
  montoEfectivo: string
  vuelto: number
  paso: 'seleccion' | 'monto' | 'resto'
  totalResto: number
}

export default function CajaPage({ params }: { params: { id: string } }) {
  const initialCart = parseInt(params.id) || 1
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('md'))
  const barcodeRef = useRef<HTMLInputElement>(null)
  const valorRef = useRef<HTMLInputElement>(null)
  const pesoRef = useRef<HTMLInputElement>(null)

  const [carritoNumero, setCarritoNumero] = useState(initialCart)
  const [items, setItems] = useState<CarritoItem[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)

  const [rapidos, setRapidos] = useState<ProductoRapido[]>([])
  const [config, setConfig] = useState<Configuracion | null>(null)
  const [barcode, setBarcode] = useState('')
  const [cantidad, setCantidad] = useState(1)
  const [searchResults, setSearchResults] = useState<ProductoSimple[]>([])
  const [searchIndex, setSearchIndex] = useState(-1)
  const [metodosPago, setMetodosPago] = useState<any[]>([])
  const [pagoDialog, setPagoDialog] = useState(false)
  const [snack, setSnack] = useState<{ msg: string; severity: 'success' | 'error' | 'info' } | null>(null)
  const [bigAlert, setBigAlert] = useState<{ msg: string; severity: 'success' | 'error' | 'info' } | null>(null)
  const [processing, setProcessing] = useState(false)
  const [pesoDialog, setPesoDialog] = useState(false)
  const [pesoProducto, setPesoProducto] = useState<ProductoSimple | null>(null)
  const [pesoValor, setPesoValor] = useState('')
  const [valorDialog, setValorDialog] = useState(false)
  const [valorProducto, setValorProducto] = useState<ProductoSimple | null>(null)
  const [valorCustom, setValorCustom] = useState('')
  const [authDialog, setAuthDialog] = useState<{ open: boolean; titulo?: string; mensaje?: string; accion?: string; onSuccess: (clave: string) => void }>({ open: false, onSuccess: () => {} })
  const [shortcutsMenu, setShortcutsMenu] = useState<null | HTMLElement>(null)
  const [showMobileCart, setShowMobileCart] = useState(true)
  const [pago, setPago] = useState<PagoState>({ metodo: '', montoEfectivo: '', vuelto: 0, paso: 'seleccion', totalResto: 0 })
  const [prefixMode, setPrefixMode] = useState(false)
  const [cartsWithItems, setCartsWithItems] = useState<number[]>([])

  const showAlert = (msg: string, severity: 'success' | 'error' | 'info') => {
    setBigAlert({ msg, severity })
  }

  const switchCart = useCallback((n: number) => {
    setCarritoNumero(n)
    window.history.replaceState(null, '', `/caja/${n}`)
    setSearchResults([])
    setBarcode('')
  }, [])

  const loadData = useCallback(async () => {
    try {
      const [itemsRes, rapidosRes, configRes, metodosRes] = await Promise.all([
        carritoAPI.list(carritoNumero), productosAPI.rapidos(),
        configAPI.get(), metodosPagoAPI.list(),
      ])
      setItems(itemsRes.data.results || itemsRes.data)
      setRapidos(rapidosRes.data.results || rapidosRes.data)
      setConfig(configRes.data)
      setMetodosPago(metodosRes.data)
      const t = await carritoAPI.total(carritoNumero)
      setTotal(t.data.total)
      // Load which carts have items
      try { const n = await carritoAPI.numeros(); setCartsWithItems(n.data) } catch {}
    } catch { /* ignore */ } finally { setLoading(false) }
  }, [carritoNumero])

  useEffect(() => { loadData() }, [loadData])
  useEffect(() => { setTimeout(() => barcodeRef.current?.focus(), 100) }, [carritoNumero])
  useEffect(() => { const iv = setInterval(loadData, 30000); return () => clearInterval(iv) }, [loadData])
  useEffect(() => { if (valorDialog) setTimeout(() => valorRef.current?.focus(), 150) }, [valorDialog])
  useEffect(() => { if (pesoDialog) setTimeout(() => pesoRef.current?.focus(), 150) }, [pesoDialog])

  // ─── Keyboard Shortcuts ─────────────────────────────
  useKeyboardShortcuts({
    'F1': () => switchCart(1), 'F2': () => switchCart(2), 'F3': () => switchCart(3),
    'F4': () => switchCart(4), 'F5': () => switchCart(5), 'F6': () => switchCart(6),
    'F7': () => switchCart(7), 'F8': () => switchCart(8),
    'F9': async () => { try { const r = await carritoAPI.nuevo(); if (r.data.carrito_numero) switchCart(r.data.carrito_numero) } catch {} },
    'F10': () => { if (items.length > 0 && total > 0) handleOpenPago() },
    'Ctrl+D': () => setAuthDialog({ open: true, titulo: 'Abrir cajón', mensaje: 'Ingresa tu clave para abrir el cajón', accion: 'Abrir', onSuccess: (clave: string) => abrirCajon(clave) }),
    ...Object.fromEntries(metodosPago.slice(0, 9).map((mp: any, i: number) => [
      `${i + 1}`, () => { if (pagoDialog && pago.paso === 'seleccion') handleSelectMetodo(mp.codigo) }
    ])),
    '-': () => setPrefixMode(true),
  }, true)

  // Prefix mode: tecla - + tecla (busca por tecla, no índice)
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (prefixMode) {
        const key = e.key.toUpperCase()
        if (key.length === 1 && !['SHIFT', 'CONTROL', 'ALT'].includes(key)) {
          e.preventDefault()
          const rp = rapidos.find(r => r.tecla?.toUpperCase() === key)
          if (rp) addProduct(rp.producto)
          setPrefixMode(false)
        }
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [prefixMode, rapidos])

  // ─── Barcode ────────────────────────────────────────
  const handleBarcode = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!barcode.trim()) return
    try {
      const res = await productosAPI.search(barcode.trim())
      if (res.data.length === 1) {
        const p = res.data[0]
        if (p.tipo_venta === 'gramaje') { setPesoProducto(p); setPesoValor(''); setPesoDialog(true) }
        else if (p.tipo_venta === 'valor') { setValorProducto(p); setValorCustom(''); setValorDialog(true) }
        else { await carritoAPI.agregar(p.id_producto, cantidad, carritoNumero); setBarcode(''); setCantidad(1); loadData() }
      } else if (res.data.length > 1) { setSearchResults(res.data); setSearchIndex(-1) }
      else { showAlert('Producto no encontrado', 'error') }
    } catch { showAlert('Error al buscar', 'error') }
  }

  useEffect(() => {
    const h = (e: KeyboardEvent) => {
      if (searchResults.length === 0) return
      if (e.key === 'ArrowDown') { e.preventDefault(); setSearchIndex(i => Math.min(i + 1, searchResults.length - 1)) }
      if (e.key === 'ArrowUp') { e.preventDefault(); setSearchIndex(i => Math.max(i - 1, 0)) }
      if ((e.key === 'Enter' || e.key === 'Tab') && searchIndex >= 0 && searchResults[searchIndex]) {
        e.preventDefault(); addProduct(searchResults[searchIndex])
      }
    }
    window.addEventListener('keydown', h); return () => window.removeEventListener('keydown', h)
  }, [searchResults, searchIndex])

  const addProduct = async (p: ProductoSimple | { id_producto: number; tipo_venta: string }) => {
    if (p.tipo_venta === 'gramaje') {
      setPesoProducto(p as ProductoSimple); setPesoValor(''); setPesoDialog(true)
    } else if (p.tipo_venta === 'valor') {
      setValorProducto(p as ProductoSimple); setValorCustom(''); setValorDialog(true)
    } else {
      await carritoAPI.agregar(p.id_producto, 1, carritoNumero)
    }
    setSearchResults([]); barcodeRef.current?.focus(); loadData()
  }

  const updateCantidad = async (item: CarritoItem, delta: number) => {
    const nc = (item.cantidad || 0) + delta
    if (nc <= 0) { await carritoAPI.delete(item.id); loadData(); return }
    await carritoAPI.agregar(item.producto.id_producto, delta, carritoNumero); loadData()
  }

  const removeItem = async (id: number) => { await carritoAPI.delete(id); loadData() }
  const clearCart = async () => { await carritoAPI.vaciar(carritoNumero); loadData() }
  const focusBarcode = () => setTimeout(() => barcodeRef.current?.focus(), 50)
  const handleAddValor = async () => {
    if (!valorProducto || !valorCustom) return
    await carritoAPI.agregar(valorProducto.id_producto, 1, carritoNumero, { valor: parseFloat(valorCustom) })
    setValorDialog(false); setValorProducto(null); setValorCustom(''); loadData()
    focusBarcode()
  }
  const handleAddPeso = async () => {
    if (!pesoProducto || !pesoValor) return
    await carritoAPI.agregar(pesoProducto.id_producto, 0, carritoNumero, { gramaje: parseFloat(pesoValor) })
    setPesoDialog(false); setPesoProducto(null); setPesoValor(''); loadData()
    focusBarcode()
  }

  const abrirCajon = async (clave: string) => {
    setAuthDialog({ open: false, onSuccess: () => {} })
    setProcessing(true)
    try { const res = await autorizacionAPI.abrirCajon(clave); showAlert('Cajón abierto', 'success') }
    catch (err: any) { showAlert(err.response?.data?.error || 'Error', 'error') }
    finally { setProcessing(false) }
  }

  // ─── Payment ────────────────────────────────────────
  const handleOpenPago = () => {
    if (total <= 0) { showAlert('El total debe ser mayor a $0', 'error'); return }
    setPago({ metodo: '', montoEfectivo: '', vuelto: 0, paso: 'seleccion', totalResto: 0 })
    setPagoDialog(true)
  }

  const getMetodo = (codigo: string) => metodosPago.find((m: any) => m.codigo === codigo)

  const handleSelectMetodo = (codigo: string) => {
    const mp = getMetodo(codigo)
    if (mp?.requiere_autorizacion) {
      setAuthDialog({ open: true, titulo: 'Autorizar pago', mensaje: `Ingresa tu clave para pagar con ${mp.nombre}`, accion: 'Pagar', onSuccess: (clave: string) => {
        setAuthDialog(a => ({ ...a, open: false }))
        if (mp.pide_monto) setPago(p => ({ ...p, metodo: codigo, paso: 'monto' }))
        else confirmarPago(codigo, 0, 0, clave)
      }})
      return
    }
    if (mp?.pide_monto) setPago(p => ({ ...p, metodo: codigo, paso: 'monto' }))
    else confirmarPago(codigo, 0, 0)
  }

  const confirmarPago = async (metodo: string, restante: number, vuelto: number, clave?: string) => {
    setProcessing(true)
    try {
      const mp = getMetodo(metodo)
      const payload: any = {
        tipo_pago: metodo,
        carrito_numero: carritoNumero,
        restante,
        vuelto_inicial: vuelto,
        abre_gaveta: mp?.abre_gaveta || false,
      }
      if (clave) payload.clave_anulacion = clave
      await ventasAPI.generar(payload)
      const msg = vuelto > 0 ? `Venta realizada! Vuelto: ${formatMoney(vuelto)}` : 'Venta realizada!'
      setPagoDialog(false)
      showAlert(msg, 'success')
      setBarcode(''); barcodeRef.current?.focus(); loadData()
    } catch { showAlert('Error al procesar venta', 'error') }
    finally { setProcessing(false) }
  }

  const cartColors = useMemo(() => {
    if (typeof window === 'undefined') return { active: '#6366f1', hasItems: '#10b981', empty: '#64748b' }
    try {
      return {
        active: localStorage.getItem('cart-color-active') || '#6366f1',
        hasItems: localStorage.getItem('cart-color-hasitems') || '#10b981',
        empty: localStorage.getItem('cart-color-empty') || '#64748b',
      }
    } catch { return { active: '#6366f1', hasItems: '#10b981', empty: '#64748b' } }
  }, [])

  if (loading) return <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh"><CircularProgress /></Box>

  const quickWithKeys = rapidos.filter(r => r.tecla).slice(0, 10)

  return (
    <Box sx={{ animation: 'fadeIn 0.3s ease' }}>
      {/* ═══ BIG ALERT ═══ */}
      <BigAlert open={!!bigAlert} message={bigAlert?.msg || ''} severity={bigAlert?.severity || 'info'}
        onClose={() => setBigAlert(null)} />

      {/* TABS */}
      <Paper sx={{ mb: 2, borderRadius: 3, overflow: 'hidden', border: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', px: 1 }}>
          <Box display="flex" gap={0.5} sx={{ p: 0.5, flex: 1, overflow: 'auto' }}>
            {[1,2,3,4,5,6,7,8].map(n => {
              const isActive = n === carritoNumero
              const hasItems = cartsWithItems?.includes(n)
              const tabColor = isActive ? cartColors.active : (hasItems ? cartColors.hasItems : cartColors.empty)
              return (
                <Button key={n} onClick={() => switchCart(n)}
                  variant={isActive ? 'contained' : 'outlined'}
                  size="small"
                  sx={{
                    minWidth: 72, px: 1.2, py: 0.6, borderRadius: 2, flexShrink: 0,
                    display: 'flex', flexDirection: 'column', gap: 0, lineHeight: 1.2,
                    bgcolor: isActive ? tabColor : 'transparent',
                    borderColor: tabColor,
                    color: isActive ? '#fff' : tabColor,
                    '&:hover': { bgcolor: isActive ? tabColor : `${tabColor}15` },
                    transition: 'all 0.15s ease',
                  }}>
                  <Typography variant="caption" fontWeight={700} fontSize="0.75rem">Caja {n}</Typography>
                  <Typography variant="caption" sx={{ opacity: 0.7, fontSize: '0.6rem' }}>F{n}</Typography>
                </Button>
              )
            })}
          </Box>
          <Box display="flex" gap={0.5} ml={1}>
            <Tooltip title="Abrir cajón (Ctrl+D)"><IconButton size="small" onClick={() => setAuthDialog({ open: true, titulo: 'Abrir cajón', mensaje: 'Ingresa tu clave para abrir el cajón', accion: 'Abrir', onSuccess: (clave: string) => abrirCajon(clave) })}
              sx={{ bgcolor: alpha(theme.palette.warning.main, 0.1) }}><Casino fontSize="small" /></IconButton></Tooltip>
            <Tooltip title="Atajos"><IconButton size="small" onClick={(e) => setShortcutsMenu(e.currentTarget)}>
              <KeyboardAlt fontSize="small" /></IconButton></Tooltip>
          </Box>
        </Box>
      </Paper>

      {/* Mobile toggle */}
      {isMobile && (
        <Box display="flex" gap={1} mb={1.5}>
          <Button fullWidth variant={showMobileCart ? 'contained' : 'outlined'} size="small"
            onClick={() => setShowMobileCart(true)} startIcon={<ShoppingCart />}>Carrito</Button>
          <Button fullWidth variant={!showMobileCart ? 'contained' : 'outlined'} size="small"
            onClick={() => setShowMobileCart(false)} startIcon={<Speed />}>Rápidos</Button>
        </Box>
      )}

      <Grid container spacing={2}>
        {/* ─── LEFT: CART ─────────────────────────────── */}
        <Grid item xs={12} md={7} lg={8} sx={{ display: { xs: showMobileCart ? 'block' : 'none', md: 'block' } }}>
          <Card sx={{ height: '100%' }}>
            <CardContent sx={{ p: { xs: 1.5, sm: 2, md: 2.5 } }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1.5}>
                <Box display="flex" alignItems="center" gap={1}>
                  <ShoppingCart color="primary" />
                  <Typography variant="h6" fontWeight={700}>Carrito #{carritoNumero}</Typography>
                  <Chip label={`${items.length} item(s)`} size="small" variant="outlined" />
                </Box>
                {items.length > 0 && (
                  <Button size="small" color="error" onClick={clearCart} startIcon={<Delete />} sx={{ borderRadius: 2, display: { xs: 'none', sm: 'flex' } }}>Vaciar</Button>
                )}
              </Box>

              <Paper component="form" onSubmit={handleBarcode} elevation={0} sx={{
                mb: 1.5, display: 'flex', alignItems: 'center',
                border: 2, borderColor: alpha(theme.palette.primary.main, 0.15), borderRadius: 3,
                bgcolor: alpha(theme.palette.primary.main, 0.03),
                '&:focus-within': { borderColor: 'primary.main', boxShadow: `0 0 0 4px ${alpha(theme.palette.primary.main, 0.1)}` },
              }}>
                <Box sx={{ px: 1.5, color: 'text.disabled', display: { xs: 'none', sm: 'flex' } }}><QrCodeScanner /></Box>
                <TextField fullWidth placeholder="Código de barras"
                  value={barcode} onChange={async (e) => {
                    setBarcode(e.target.value)
                    if (e.target.value.trim().length >= 2) {
                      try { const r = await productosAPI.search(e.target.value.trim()); setSearchResults(r.data); setSearchIndex(-1) }
                      catch {}
                    } else { setSearchResults([]) }
                  }}
                  inputRef={barcodeRef} variant="standard" InputProps={{ disableUnderline: true }}
                  sx={{ '& .MuiInputBase-root': { py: 1.2, fontSize: { xs: '0.9rem', sm: '1rem' } } }} />
                <Box sx={{ pr: 1 }}>
                  <Button type="submit" variant="contained" aria-label="Buscar" sx={{ borderRadius: 2, minWidth: 36, px: 1.5, height: 34 }}><Search /></Button>
                </Box>
              </Paper>

              {searchResults.length > 0 && (
                <Paper sx={{ mb: 1.5, borderRadius: 2, maxHeight: 200, overflow: 'auto', border: 1, borderColor: 'divider' }}>
                  <List dense disablePadding>
                    {searchResults.map((p, i) => (
                      <ListItemButton key={p.id_producto} selected={i === searchIndex} onClick={() => addProduct(p)}
                        sx={{ borderBottom: 1, borderColor: 'divider', '&:last-child': { borderBottom: 0 }, py: 1.2 }}>
                        <ListItemText primary={<Typography fontWeight={600}>{p.nombre}</Typography>}
                          secondary={
                            <Box component="span" display="flex" alignItems="center" gap={1} mt={0.3}>
                              <Typography component="span" variant="body2" color="primary.main" fontWeight={700}>
                                {formatMoney(p.precio)}
                              </Typography>
                              <Chip label={p.tipo_venta} size="small" variant="outlined" sx={{ height: 18 }} />
                            </Box>} />
                        <Box display="flex" gap={0.5} alignItems="center">
                          <Tooltip title={rapidos.find(r => r.producto.id_producto === p.id_producto) ? 'Quitar de rápidos' : rapidos.length >= 10 ? 'Máximo 10 rápidos' : 'Agregar a rápidos'}>
                            <IconButton size="small" onClick={async (e) => {
                              e.stopPropagation()
                              const exists = rapidos.find(r => r.producto.id_producto === p.id_producto)
                              if (exists) await productosAPI.eliminarRapido(p.id_producto)
                              else if (rapidos.length < 10) {
                                await productosAPI.agregarRapido(p.id_producto)
                              } else { showAlert('Máximo 10 productos rápidos', 'error'); return }
                              const r = await productosAPI.rapidos()
                              setRapidos(r.data.results || r.data)
                            }}>
                              {rapidos.find(r => r.producto.id_producto === p.id_producto)
                                ? <Star sx={{ color: theme.palette.warning.main }} fontSize="small" />
                                : <StarBorder fontSize="small" />}
                            </IconButton>
                          </Tooltip>
                          <Chip label="+Agregar" size="small" color="primary" clickable onClick={() => addProduct(p)} />
                        </Box>
                      </ListItemButton>
                    ))}
                  </List>
                </Paper>
              )}

              {items.length === 0 ? (
                <Box textAlign="center" py={{ xs: 4, sm: 6 }}>
                  <ShoppingCart sx={{ fontSize: 48, color: 'text.disabled', mb: 1 }} />
                  <Typography color="text.secondary">Carrito vacío</Typography>
                  <Typography variant="body2" color="text.disabled">Escanea o usa los rápidos</Typography>
                </Box>
              ) : (
                <TableContainer sx={{ display: { xs: 'none', sm: 'block' }, borderRadius: 2, border: 1, borderColor: 'divider' }}>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell width="38%">Producto</TableCell>
                        <TableCell align="center" width="28%">Cantidad</TableCell>
                        <TableCell align="right" width="20%">Subtotal</TableCell>
                        <TableCell align="right" width="14%"></TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {items.map((item) => (
                        <TableRow key={item.id} hover>
                          <TableCell>
                            <Typography variant="body2" fontWeight={600}>{item.producto.nombre}</Typography>
                            <Typography variant="caption" color="text.secondary">{formatMoney(item.producto.precio)}/ud.</Typography>
                          </TableCell>
                          <TableCell align="center">
                            <Box display="inline-flex" alignItems="center" gap={0.3} sx={{ border: 1, borderColor: 'divider', borderRadius: 2, px: 0.3, py: 0.1 }}>
                              <IconButton size="small" onClick={() => updateCantidad(item, -1)} sx={{ color: 'error.main' }}><Remove fontSize="small" /></IconButton>
                              <Typography fontWeight={800} mx={0.8} minWidth={30} textAlign="center" variant="h6" sx={{ fontSize: { xs: '1rem', sm: '1.15rem' } }}>
                                {item.cantidad || (item.gramaje ? `${item.gramaje}g` : '0')}
                              </Typography>
                              <IconButton size="small" onClick={() => updateCantidad(item, 1)} sx={{ color: 'primary.main' }}><Add fontSize="small" /></IconButton>
                            </Box>
                          </TableCell>
                          <TableCell align="right"><Typography fontWeight={700} color="primary.main">{formatMoney(item.subtotal)}</Typography></TableCell>
                          <TableCell align="right">
                            <IconButton size="small" onClick={() => removeItem(item.id)} sx={{ color: 'error.main', opacity: 0.5, '&:hover': { opacity: 1 } }}><Delete fontSize="small" /></IconButton>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}

              <Box sx={{ display: { xs: 'block', sm: 'none' } }}>
                {items.map((item) => (
                  <Paper key={item.id} elevation={0} sx={{ p: 1.5, mb: 1, borderRadius: 2, border: 1, borderColor: 'divider' }}>
                    <Box display="flex" justifyContent="space-between" mb={0.5}>
                      <Typography variant="body2" fontWeight={700}>{item.producto.nombre}</Typography>
                      <Typography variant="h6" fontWeight={800} color="primary.main">{formatMoney(item.subtotal)}</Typography>
                    </Box>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box display="flex" alignItems="center" gap={0.5} sx={{ border: 1, borderColor: 'divider', borderRadius: 2, px: 0.5, py: 0.2 }}>
                        <IconButton size="small" onClick={() => updateCantidad(item, -1)} color="error"><Remove fontSize="small" /></IconButton>
                        <Typography fontWeight={800} sx={{ fontSize: '1.1rem', minWidth: 28, textAlign: 'center' }}>{item.cantidad || `${item.gramaje}g`}</Typography>
                        <IconButton size="small" onClick={() => updateCantidad(item, 1)} color="primary"><Add fontSize="small" /></IconButton>
                      </Box>
                      <IconButton size="small" onClick={() => removeItem(item.id)} color="error"><Delete fontSize="small" /></IconButton>
                    </Box>
                  </Paper>
                ))}
              </Box>

              <Box sx={{ mt: 2, pt: 2, borderTop: 2, borderColor: alpha(theme.palette.primary.main, 0.1) }}>
                <Box display="flex" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={1}>
                  <Typography variant="body2" color="text.secondary">{items.length} productos</Typography>
                  <Box textAlign="right">
                    <Typography variant="caption" color="text.secondary" fontWeight={600}>TOTAL</Typography>
                    <Typography variant="h3" fontWeight={800} color="primary.main" sx={{ fontSize: { xs: '1.75rem', sm: '2.25rem' }, lineHeight: 1.1 }}>
                      {formatMoney(total)}
                    </Typography>
                  </Box>
                </Box>
                <Button fullWidth variant="contained" size="large" disabled={items.length === 0 || total <= 0}
                  onClick={handleOpenPago}
                  sx={{ mt: 2, py: 1.8, fontSize: { xs: '1rem', sm: '1.15rem' }, fontWeight: 700, borderRadius: 3,
                    background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`, }}
                  startIcon={<Payment />}>
                  Cobrar{total > 0 ? `  ·  ${formatMoney(total)}` : ''}
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* ─── RIGHT: RÁPIDOS + PAGO ──────────────────── */}
        <Grid item xs={12} md={5} lg={4} sx={{ display: { xs: !showMobileCart ? 'block' : 'none', md: 'block' } }}>
          <Card sx={{ mb: 2 }}>
            <CardContent sx={{ p: { xs: 1.5, sm: 2 } }}>
              <Box display="flex" alignItems="center" gap={1} mb={1.5}>
                <Speed color="primary" />
                <Typography fontWeight={700} sx={{ fontSize: '1rem' }}>Rápidos</Typography>
                {prefixMode && <Chip label="Presiona 0-9" size="small" color="warning" sx={{ animation: 'pulse 1s infinite' }} />}
              </Box>
              {rapidos.length === 0 ? (
                <Typography variant="body2" color="text.disabled" textAlign="center" py={2}>
                  Busca un producto y haz clic en ⭐
                </Typography>
              ) : (
                <Grid container spacing={1}>
                  {rapidos.map((rp) => (
                    <Grid item xs={4} sm={3} md={6} key={rp.id}>
                      <Button variant="outlined" fullWidth
                        onClick={() => addProduct(rp.producto)}
                        sx={{
                          p: 1, borderRadius: 2, textAlign: 'center', flexDirection: 'column', gap: 0.2,
                          borderColor: 'divider', minHeight: 66, position: 'relative',
                          bgcolor: alpha(theme.palette.primary.main, 0.03),
                          '&:hover': { borderColor: 'primary.main', bgcolor: alpha(theme.palette.primary.main, 0.08), transform: 'translateY(-1px)' },
                          transition: 'all 0.15s ease',
                        }}>
                        {rp.tecla && (
                          <Box sx={{ position: 'absolute', top: -4, right: -4, width: 22, height: 22, borderRadius: '50%',
                            bgcolor: prefixMode ? theme.palette.warning.main : theme.palette.primary.main,
                            color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center',
                            fontSize: 11, fontWeight: 800, boxShadow: 2 }}>
                            {rp.tecla}
                          </Box>
                        )}
                        <Typography variant="body2" fontWeight={700} noWrap lineHeight={1.2}>{rp.producto.nombre}</Typography>
                        <Box display="flex" alignItems="center" justifyContent="center" gap={0.5} mt={0.2}>
                          <Typography variant="body2" fontWeight={800} color="primary.main" sx={{ fontSize: { xs: '0.75rem', sm: '0.85rem' } }}>
                            {formatMoney(rp.producto.precio)}
                          </Typography>
                          <Chip label={rp.producto.tipo_venta} size="small"
                            color={rp.producto.tipo_venta === 'unidad' ? 'default' : rp.producto.tipo_venta === 'gramaje' ? 'info' : 'warning'}
                            variant="outlined" sx={{ height: 16, fontSize: 8, fontWeight: 600 }} />
                        </Box>
                      </Button>
                    </Grid>
                  ))}
                </Grid>
              )}
              <Typography variant="caption" color="text.disabled" display="block" textAlign="center" mt={1}>
                Presiona <strong>-</strong> luego el <strong>número</strong>
              </Typography>
            </CardContent>
          </Card>

          <Card>
            <CardContent sx={{ p: { xs: 1.5, sm: 2 }, textAlign: 'center' }}>
              <Box display="flex" alignItems="center" justifyContent="center" gap={1} mb={2}>
                <Casino color="warning" />
                <Typography variant="subtitle1" fontWeight={700}>Cajón</Typography>
              </Box>
              <Button fullWidth variant="contained" color="warning" size="large"
                onClick={() => setAuthDialog({ open: true, titulo: 'Abrir cajón', mensaje: 'Ingresa tu clave para abrir el cajón', accion: 'Abrir', onSuccess: (clave: string) => abrirCajon(clave) })}
                startIcon={<Casino />} sx={{ borderRadius: 2, py: 1.5, fontWeight: 700 }}>
                Abrir Cajón
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* ─── DIALOGS ──────────────────────────────────── */}

      <Dialog open={pesoDialog} onClose={() => { setPesoDialog(false); focusBarcode() }} maxWidth="xs" fullWidth PaperProps={{ sx: { borderRadius: 4 } }} TransitionComponent={Zoom}>
        <DialogTitle><Typography fontWeight={700}>Ingresar peso</Typography></DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" mb={2}>{pesoProducto?.nombre}</Typography>
          <TextField fullWidth label="Peso en gramos" type="number" value={pesoValor}
            onChange={(e) => setPesoValor(e.target.value)}
            inputRef={pesoRef}
            onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleAddPeso() } }}
            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
        </DialogContent>
        <DialogActions sx={{ p: 3, pt: 0 }}>
          <Button onClick={() => { setPesoDialog(false); focusBarcode() }} sx={{ borderRadius: 2 }}>Cancelar</Button>
          <Button variant="contained" onClick={handleAddPeso} sx={{ borderRadius: 2 }}>Agregar</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={valorDialog} onClose={() => { setValorDialog(false); focusBarcode() }} maxWidth="xs" fullWidth PaperProps={{ sx: { borderRadius: 4 } }} TransitionComponent={Zoom}>
        <DialogTitle><Typography fontWeight={700}>Ingresar valor</Typography></DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" mb={2}>{valorProducto?.nombre}</Typography>
          <TextField fullWidth label="Valor personalizado" type="number" value={valorCustom}
            onChange={(e) => setValorCustom(e.target.value)}
            inputRef={valorRef}
            onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleAddValor() } }}
            sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
        </DialogContent>
        <DialogActions sx={{ p: 3, pt: 0 }}>
          <Button onClick={() => { setValorDialog(false); focusBarcode() }} sx={{ borderRadius: 2 }}>Cancelar</Button>
          <Button variant="contained" onClick={handleAddValor} sx={{ borderRadius: 2 }}>Agregar</Button>
        </DialogActions>
      </Dialog>

      {/* ─── PAYMENT ──────────────────────────────────── */}
      <Dialog open={pagoDialog} onClose={() => { if (!processing) { setPagoDialog(false); focusBarcode() }}} maxWidth="sm" fullWidth TransitionComponent={Zoom} PaperProps={{ sx: { borderRadius: 4 } }}>
        <DialogTitle sx={{ pb: 0 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Typography variant="h5" fontWeight={800}>Cobrar</Typography>
            <IconButton onClick={() => { setPagoDialog(false); focusBarcode() }} disabled={processing}><Close /></IconButton>
          </Box>
        </DialogTitle>
        <DialogContent sx={{ pt: 3 }}>
          <Paper elevation={0} sx={{ background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.08)}, ${alpha(theme.palette.primary.dark, 0.05)})`,
            p: 3, borderRadius: 3, textAlign: 'center', mb: 2, border: 2, borderColor: alpha(theme.palette.primary.main, 0.1) }}>
            <Typography variant="caption" fontWeight={600} color="text.secondary">Total a pagar</Typography>
            <Typography variant="h2" fontWeight={800} color="primary.main" sx={{ fontSize: { xs: '2.2rem', sm: '2.8rem' } }}>
              {formatMoney(total)}
            </Typography>
          </Paper>

          {pago.paso === 'seleccion' && (
            <><Typography variant="subtitle2" fontWeight={600} mb={1.5}>Selecciona método (usa 1-{Math.min(metodosPago.length, 9)} en teclado)</Typography>
            <Grid container spacing={1.5}>
              {metodosPago.map((mp, idx) => (
                <Grid item xs={6} key={mp.codigo}>
                  <Button fullWidth variant="outlined" size="large" onClick={() => handleSelectMetodo(mp.codigo)}
                    startIcon={getIcon(mp.icono)}
                    sx={{ py: 2, borderRadius: 2.5, fontWeight: 600, borderWidth: 2, position: 'relative',
                      borderColor: alpha(mp.color || theme.palette.primary.main, 0.3),
                      transition: 'all 0.15s',
                      '&:hover': { borderColor: mp.color || theme.palette.primary.main, bgcolor: alpha(mp.color || theme.palette.primary.main, 0.04), transform: 'translateY(-2px)' },
                    }}>
                    <Box sx={{ position: 'absolute', top: 4, right: 4, width: 20, height: 20, borderRadius: '50%',
                      bgcolor: alpha(mp.color || theme.palette.primary.main, 0.1), display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontSize: 10, fontWeight: 700, color: mp.color }}>{idx + 1}</Box>
                    {mp.nombre}
                  </Button>
                </Grid>
              ))}
            </Grid></>
          )}

          {pago.paso === 'monto' && (
            <><Typography variant="subtitle2" fontWeight={600} mb={1.5}>¿Con cuánto paga?</Typography>
            <TextField fullWidth label="Monto recibido" type="number" value={pago.montoEfectivo}
              onChange={(e) => { const m = parseFloat(e.target.value) || 0; setPago(p => ({ ...p, montoEfectivo: e.target.value, vuelto: m >= total ? m - total : 0 })) }}
              autoFocus InputProps={{ startAdornment: <InputAdornment position="start"><Typography fontWeight={700}>$</Typography></InputAdornment> }}
              sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2, fontSize: '1.5rem' }, mb: 2 }} />
            {pago.vuelto > 0 && getMetodo(pago.metodo)?.da_vuelto && (
              <Paper elevation={0} sx={{ background: `linear-gradient(135deg, ${alpha(theme.palette.success.main, 0.1)}, ${alpha(theme.palette.success.light, 0.05)})`,
                p: 2.5, borderRadius: 3, display: 'flex', justifyContent: 'space-between', border: 2, borderColor: alpha(theme.palette.success.main, 0.15) }}>
                <Typography fontWeight={700}>Vuelto</Typography>
                <Typography variant="h4" fontWeight={800} color="success.main">{formatMoney(pago.vuelto)}</Typography>
              </Paper>
            )}
            <Button fullWidth variant="contained" size="large" disabled={!pago.montoEfectivo}
              onClick={() => {
                const m = parseFloat(pago.montoEfectivo) || 0
                const mp = getMetodo(pago.metodo)
                if (m >= total) confirmarPago(pago.metodo, 0, mp?.da_vuelto ? m - total : 0)
                else setPago(p => ({ ...p, paso: 'resto', totalResto: total - m }))
              }}
              sx={{ mt: 2, py: 1.8, borderRadius: 2.5, fontWeight: 700, fontSize: '1.1rem' }}>
              {parseFloat(pago.montoEfectivo) >= total ? `Pagar ${formatMoney(total)}` : 'Pago parcial'}
            </Button></>
          )}

          {pago.paso === 'resto' && (
            <><Alert severity="info" sx={{ mb: 2, borderRadius: 2 }}>
              <Typography fontWeight={600}>Pago parcial</Typography>
              <Typography variant="body2">{formatMoney(parseFloat(pago.montoEfectivo) || 0)} pagados · Restan: {formatMoney(pago.totalResto)}</Typography>
            </Alert>
            <Typography variant="subtitle2" fontWeight={600} mb={1.5}>Completa con otro método</Typography>
            <Grid container spacing={1.5}>
              {metodosPago.filter(mp => mp.acepta_diferencia).map(mp => (
                <Grid item xs={6} key={mp.codigo}>
                  <Button fullWidth variant="outlined" size="large" onClick={() => {
                    const totalPagado = (parseFloat(pago.montoEfectivo) || 0) + pago.totalResto
                    if (mp.es_efectivo) confirmarPago(mp.codigo, 0, mp.da_vuelto ? totalPagado - total : 0)
                    else confirmarPago(mp.codigo, pago.totalResto, 0)
                  }} startIcon={getIcon(mp.icono)} sx={{ py: 2, borderRadius: 2.5, fontWeight: 600, borderWidth: 2 }}>{mp.nombre}</Button>
                </Grid>
              ))}
            </Grid></>
          )}
        </DialogContent>
      </Dialog>

      {/* Auth */}
      <AuthorizationDialog open={authDialog.open} onClose={() => setAuthDialog({ ...authDialog, open: false })}
        onSuccess={(_usuario: string, clave: string) => authDialog.onSuccess(clave)}
        titulo={authDialog.titulo} mensaje={authDialog.mensaje} accion={authDialog.accion}
        titulo="Abrir Cajón" mensaje="Ingresa tu clave" accion="Abrir" icono={<Casino />} />

      {/* Shortcuts info */}
      <Menu anchorEl={shortcutsMenu} open={!!shortcutsMenu} onClose={() => setShortcutsMenu(null)} PaperProps={{ sx: { borderRadius: 3, minWidth: 280 } }}>
        <MenuItem disabled><Typography variant="caption" fontWeight={700} color="text.secondary">ATAJOS</Typography></MenuItem>
        {[['F1-F8', 'Cambiar caja'], ['F9', 'Nueva caja'], ['F10', 'Cobrar'],
          ['Ctrl+D', 'Abrir cajón'], ['Enter', 'Buscar'], ['- + N°', 'Producto rápido'],
          ['1-4', 'Método de pago'], ['↑/↓', 'Navegar'], ['Esc', 'Cerrar'],
        ].map(([k, d]) => (
          <MenuItem key={k as string} dense sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="body2" color="text.secondary">{d}</Typography>
            <Chip label={k} size="small" variant="outlined" sx={{ fontFamily: 'monospace', fontWeight: 700, fontSize: 10 }} />
          </MenuItem>
        ))}
      </Menu>
    </Box>
  )
}
