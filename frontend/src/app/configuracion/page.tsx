'use client'
import { useState, useEffect } from 'react'
import {
  Box, Card, CardContent, Grid, TextField, Button, Typography,
  Select, MenuItem, FormControl, InputLabel, CircularProgress, Alert,
  Chip, Divider, Fade, Paper, alpha, Tooltip,
} from '@mui/material'
import { Save, Print, Settings, Build, Router, Usb, Lock, People, Person } from '@mui/icons-material'
import { configAPI, impresoraAPI } from '@/lib/api'
import { Configuracion } from '@/types'
import { useThemeMode } from '@/components/ThemeRegistry'
import { THEMES } from '@/lib/themes'

export default function ConfigPage() {
  const [config, setConfig] = useState<Configuracion | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [testMsg, setTestMsg] = useState<{ type: 'success' | 'error'; msg: string } | null>(null)
  const { themeId, setThemeId } = useThemeMode()
  const [primaryColor, setPrimaryColor] = useState('#6366f1')
  const [secondaryColor, setSecondaryColor] = useState('#10b981')
  const [fontSize, setFontSize] = useState(16)
  const [navFontSize, setNavFontSize] = useState(14)
  const [cartActiveColor, setCartActiveColor] = useState('#6366f1')
  const [cartHasItemsColor, setCartHasItemsColor] = useState('#10b981')
  const [cartEmptyColor, setCartEmptyColor] = useState('#64748b')

  const getLS = (key: string, def: string) => { try { return localStorage.getItem(key) || def } catch { return def } }

  useEffect(() => {
    try {
      setPrimaryColor(getLS('app-primary-color', '#6366f1'))
      setSecondaryColor(getLS('app-secondary-color', '#10b981'))
      setFontSize(parseInt(getLS('app-font-size', '16')))
      setNavFontSize(parseInt(getLS('app-nav-font-size', '14')))
      setCartActiveColor(getLS('cart-color-active', '#6366f1'))
      setCartHasItemsColor(getLS('cart-color-hasitems', '#10b981'))
      setCartEmptyColor(getLS('cart-color-empty', '#64748b'))
    } catch {}
    configAPI.get().then((res) => setConfig(res.data)).finally(() => setLoading(false))
  }, [])

  const applyColors = (primary: string, secondary: string) => {
    localStorage.setItem('app-primary-color', primary)
    localStorage.setItem('app-secondary-color', secondary)
    setPrimaryColor(primary)
    setSecondaryColor(secondary)
    document.documentElement.style.setProperty('--app-primary', primary)
    document.documentElement.style.setProperty('--app-secondary', secondary)
  }

  useEffect(() => {
    configAPI.get().then((res) => setConfig(res.data)).finally(() => setLoading(false))
  }, [])

  const handleSave = async () => {
    if (!config) return
    setSaving(true)
    try { await configAPI.update(config); setTestMsg({ type: 'success', msg: 'Configuración guardada exitosamente' }) }
    catch { setTestMsg({ type: 'error', msg: 'Error al guardar' }) }
    finally { setSaving(false) }
  }

  const handleTestPrint = async () => {
    try { const res = await impresoraAPI.probar(); setTestMsg({ type: 'success', msg: res.data }) }
    catch { setTestMsg({ type: 'error', msg: 'Error al probar impresora' }) }
  }

  if (loading) return <Box display="flex" justifyContent="center" py={6}><CircularProgress /></Box>
  if (!config) return <Typography>Error cargando configuración</Typography>

  return (
    <Fade in timeout={400}>
      <Box>
        <Box display="flex" alignItems="center" gap={1} mb={3}>
          <Settings color="primary" />
          <Typography variant="h4" fontWeight={700}>Configuración</Typography>
        </Box>

        {testMsg && (
          <Alert severity={testMsg.type} sx={{ mb: 2, borderRadius: 2 }} onClose={() => setTestMsg(null)}>
            {testMsg.msg}
          </Alert>
        )}

        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Card sx={{ borderRadius: 3 }}>
              <CardContent sx={{ p: 3 }}>
                <Box display="flex" alignItems="center" gap={1} mb={3}>
                  <Build color="primary" />
                  <Typography variant="h6" fontWeight={700}>Sistema</Typography>
                </Box>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <TextField fullWidth size="small" label="Decimales" type="number" value={config.decimales}
                      onChange={(e) => setConfig({ ...config, decimales: parseInt(e.target.value) })}
                      sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField fullWidth size="small" label="Clave anulación" value={config.clave_anulacion}
                      onChange={(e) => setConfig({ ...config, clave_anulacion: e.target.value })}
                      sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField fullWidth size="small" label="IVA %" type="number" value={config.porcentaje_iva}
                      onChange={(e) => setConfig({ ...config, porcentaje_iva: e.target.value })}
                      sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField fullWidth size="small" label="Tamaño letra" type="number" value={config.tamano_letra}
                      onChange={(e) => setConfig({ ...config, tamano_letra: parseInt(e.target.value) })}
                      sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
                  </Grid>
                  <Grid item xs={12}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Imprimir ticket</InputLabel>
                      <Select value={config.imprimir} label="Imprimir ticket" onChange={(e) => setConfig({ ...config, imprimir: e.target.value as any })} sx={{ borderRadius: 2 }}>
                        <MenuItem value="no">No imprimir</MenuItem>
                        <MenuItem value="con_corte">Con corte</MenuItem>
                        <MenuItem value="sin_corte">Sin corte</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card sx={{ borderRadius: 3, mb: 2 }}>
              <CardContent sx={{ p: 3 }}>
                <Box display="flex" alignItems="center" gap={1} mb={3}>
                  <Lock color="primary" />
                  <Typography variant="h6" fontWeight={700}>Autorización</Typography>
                </Box>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Modo de autorización</InputLabel>
                      <Select value={config.tipo_autorizacion} label="Modo de autorización"
                        onChange={(e) => setConfig({ ...config, tipo_autorizacion: e.target.value as any })}
                        sx={{ borderRadius: 2 }}>
                        <MenuItem value="cualquier">
                          <Box display="flex" alignItems="center" gap={1}>
                            <People fontSize="small" />
                            Cualquier usuario con clave
                          </Box>
                        </MenuItem>
                        <MenuItem value="propio">
                          <Box display="flex" alignItems="center" gap={1}>
                            <Person fontSize="small" />
                            Solo clave del usuario actual
                          </Box>
                        </MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12}>
                    <Paper elevation={0} sx={{
                      p: 2, borderRadius: 2,
                      bgcolor: (theme) => alpha(theme.palette.info.main, config.tipo_autorizacion === 'cualquier' ? 0.05 : 0.08),
                    }}>
                      <Typography variant="body2" color="text.secondary">
                        {config.tipo_autorizacion === 'cualquier'
                          ? 'Cualquier usuario registrado con una clave de anulación válida podrá autorizar acciones (abrir cajón, anular ventas, gastos)'
                          : 'Solo el usuario que inició sesión podrá autorizar acciones con su propia clave de anulación'}
                      </Typography>
                    </Paper>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
            {/* Apariencia */}
            <Card sx={{ borderRadius: 3, mb: 2 }}>
              <CardContent sx={{ p: 3 }}>
                <Box display="flex" alignItems="center" gap={1} mb={3}>
                  <Box sx={{ width: 16, height: 16, borderRadius: 1, bgcolor: primaryColor }} />
                  <Typography variant="h6" fontWeight={700}>Apariencia</Typography>
                </Box>
                <Grid container spacing={2} alignItems="end">
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" fontWeight={600} mb={1}>Tema predefinido</Typography>
                    <Box display="flex" gap={1} flexWrap="wrap">
                      {THEMES.map(t => (
                        <Chip key={t.id} label={t.name} clickable color={themeId === t.id ? 'primary' : 'default'}
                          onClick={() => { setThemeId(t.id); localStorage.setItem('app-theme-id', t.id) }}
                          sx={{ borderRadius: 1, fontWeight: 600 }} />
                      ))}
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <input type="color" value={primaryColor} onChange={(e) => applyColors(e.target.value, secondaryColor)}
                        style={{ width: 40, height: 40, border: 'none', borderRadius: 8, cursor: 'pointer', padding: 0 }} />
                      <Box>
                        <Typography variant="caption" color="text.secondary">Color primario</Typography>
                        <Typography variant="body2" fontWeight={600} sx={{ fontFamily: 'monospace' }}>{primaryColor}</Typography>
                      </Box>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <input type="color" value={secondaryColor} onChange={(e) => applyColors(primaryColor, e.target.value)}
                        style={{ width: 40, height: 40, border: 'none', borderRadius: 8, cursor: 'pointer', padding: 0 }} />
                      <Box>
                        <Typography variant="caption" color="text.secondary">Color secundario</Typography>
                        <Typography variant="body2" fontWeight={600} sx={{ fontFamily: 'monospace' }}>{secondaryColor}</Typography>
                      </Box>
                    </Box>
                  </Grid>
                  <Grid item xs={12}>
                    <Paper elevation={0} sx={{ p: 2, borderRadius: 2, bgcolor: (theme: any) => alpha(theme.palette.primary.main, 0.03) }}>
                      <Typography variant="body2" fontWeight={600} mb={1}>Tamaño de fuente — contenido</Typography>
                      <Box display="flex" alignItems="center" gap={2}>
                        <Typography variant="caption">10px</Typography>
                        <input type="range" min={10} max={24} step={1} value={fontSize}
                          onChange={(e) => {
                            const v = parseInt(e.target.value)
                            setFontSize(v)
                            localStorage.setItem('app-font-size', v.toString())
                            window.dispatchEvent(new Event('fontsizechange'))
                          }}
                          style={{ flex: 1, height: 6, accentColor: primaryColor }} />
                        <Typography variant="caption">24px</Typography>
                        <Typography fontWeight={700} minWidth={40} textAlign="center">{fontSize}px</Typography>
                      </Box>
                    </Paper>
                  </Grid>
                  <Grid item xs={12}>
                    <Paper elevation={0} sx={{ p: 2, borderRadius: 2, bgcolor: (theme: any) => alpha(theme.palette.secondary.main, 0.03) }}>
                      <Typography variant="body2" fontWeight={600} mb={1}>Tamaño de fuente — menú lateral</Typography>
                      <Box display="flex" alignItems="center" gap={2}>
                        <Typography variant="caption">10px</Typography>
                        <input type="range" min={10} max={20} step={1} value={navFontSize}
                          onChange={(e) => {
                            const v = parseInt(e.target.value)
                            setNavFontSize(v)
                            localStorage.setItem('app-nav-font-size', v.toString())
                            window.dispatchEvent(new Event('navfontsizechange'))
                          }}
                          style={{ flex: 1, height: 6, accentColor: secondaryColor }} />
                        <Typography variant="caption">20px</Typography>
                        <Typography fontWeight={700} minWidth={40} textAlign="center">{navFontSize}px</Typography>
                      </Box>
                    </Paper>
                  </Grid>
                  <Grid item xs={12}>
                    <Divider sx={{ my: 1 }} />
                    <Typography variant="subtitle2" fontWeight={600} mb={1}>Colores de cajas (tabs)</Typography>
                  </Grid>
                  {[
                    { label: 'Caja activa (con items)', key: 'cart-color-active', state: cartActiveColor, set: setCartActiveColor },
                    { label: 'Caja inactiva (con items)', key: 'cart-color-hasitems', state: cartHasItemsColor, set: setCartHasItemsColor },
                    { label: 'Caja vacía', key: 'cart-color-empty', state: cartEmptyColor, set: setCartEmptyColor },
                  ].map((c) => (
                    <Grid item xs={4} key={c.key}>
                      <Box display="flex" flexDirection="column" alignItems="center" gap={0.5}>
                        <input type="color" value={c.state}
                          onChange={(e) => {
                            c.set(e.target.value)
                            localStorage.setItem(c.key, e.target.value)
                          }}
                          style={{ width: 36, height: 36, border: 'none', borderRadius: 6, cursor: 'pointer', padding: 0 }} />
                        <Typography variant="caption" color="text.secondary" textAlign="center">{c.label}</Typography>
                      </Box>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
            <Card sx={{ borderRadius: 3 }}>
              <CardContent sx={{ p: 3 }}>
                <Box display="flex" alignItems="center" gap={1} mb={3}>
                  <Router color="primary" />
                  <Typography variant="h6" fontWeight={700}>Impresora</Typography>
                </Box>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Tipo de conexión</InputLabel>
                      <Select value={config.tipo_impresora} label="Tipo de conexión"
                        onChange={(e) => setConfig({ ...config, tipo_impresora: e.target.value as any })}
                        sx={{ borderRadius: 2 }}>
                        <MenuItem value="usb"><Usb sx={{ mr: 1, fontSize: 18 }} />USB</MenuItem>
                        <MenuItem value="ip"><Router sx={{ mr: 1, fontSize: 18 }} />IP / Red</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  {config.tipo_impresora === 'ip' && (
                    <>
                      <Grid item xs={8}>
                        <TextField fullWidth size="small" label="Dirección IP" value={config.ip_impresora}
                          onChange={(e) => setConfig({ ...config, ip_impresora: e.target.value })}
                          sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
                      </Grid>
                      <Grid item xs={4}>
                        <TextField fullWidth size="small" label="Puerto" type="number" value={config.puerto_impresora}
                          onChange={(e) => setConfig({ ...config, puerto_impresora: parseInt(e.target.value) })}
                          sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
                      </Grid>
                    </>
                  )}
                  {config.tipo_impresora === 'usb' && (
                    <Grid item xs={12}>
                      <Paper elevation={0} sx={{ bgcolor: (theme) => alpha(theme.palette.info.main, 0.05), p: 2, borderRadius: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          <Usb sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'middle' }} />
                          La impresora USB se detectará automáticamente en <Chip label="/dev/usb/lp*" size="small" sx={{ fontFamily: 'monospace' }} />
                        </Typography>
                      </Paper>
                    </Grid>
                  )}
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Box display="flex" gap={2} mt={3} justifyContent="flex-end">
          <Button variant="outlined" startIcon={<Print />} onClick={handleTestPrint} sx={{ borderRadius: 2 }}>
            Probar Impresora
          </Button>
          <Button variant="contained" startIcon={<Save />} onClick={handleSave} disabled={saving} sx={{ borderRadius: 2, px: 4 }}>
            {saving ? 'Guardando...' : 'Guardar Cambios'}
          </Button>
        </Box>
      </Box>
    </Fade>
  )
}
