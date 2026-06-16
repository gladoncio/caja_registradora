'use client'
import { useState, useEffect } from 'react'
import {
  Box, AppBar, Toolbar, Typography, Drawer, IconButton, Avatar, Tooltip,
  Menu, MenuItem, ListItemIcon, alpha, Collapse, List, ListItemButton,
  ListItemText, Divider,
} from '@mui/material'
import {
  Menu as MenuIcon, Store, DarkMode, LightMode, Logout,
  PointOfSale, Search, ShoppingCart, LockOpen, Receipt, LocalAtm,
  AccountBalanceWallet, SystemUpdate, Info, Assessment, Speed,
  AdminPanelSettings, QrCode, People, CreditCard, Inventory,
  CalendarMonth, FileUpload, ExpandLess, ExpandMore, Settings, Keyboard, History,
  Home, ListAlt, Build, Category, Star,
} from '@mui/icons-material'
import { useAuth } from '@/contexts/AuthContext'
import { useThemeMode } from './ThemeRegistry'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

const DRAWER_WIDTH = 280

interface MenuGroup {
  label: string
  icon?: React.ReactNode
  adminOnly?: boolean
  items: { label: string; icon: React.ReactNode; href: string; adminOnly?: boolean }[]
}

const menuGroups: MenuGroup[] = [
  {
    label: 'PUNTO DE VENTA', icon: <PointOfSale />,
    items: [
      { label: 'Caja', icon: <PointOfSale />, href: '/caja/1' },
      { label: 'Buscador de Precios', icon: <Search />, href: '/busqueda' },
      { label: 'Ventas del día', icon: <ShoppingCart />, href: '/ventas' },
      { label: 'Anulaciones', icon: <Receipt />, href: '/ventas/respaldo' },
    ],
  },
  {
    label: 'CAJA Y REPORTES', icon: <AccountBalanceWallet />,
    items: [
      { label: 'Abrir Caja', icon: <LockOpen />, href: '/abrir-caja' },
      { label: 'Caja Diaria', icon: <AccountBalanceWallet />, href: '/caja-diaria' },
      { label: 'Gastos', icon: <LocalAtm />, href: '/gastos' },
      { label: 'Informe de Caja', icon: <Assessment />, href: '/reportes' },
      { label: 'Cuadrar Caja', icon: <Speed />, href: '/cuadre' },
      { label: 'Detalle de un Día', icon: <CalendarMonth />, href: '/reportes/calendario' },
    ],
  },
  {
    label: 'ADMINISTRACIÓN', icon: <Build />, adminOnly: true,
    items: [
      { label: 'Productos', icon: <Inventory />, href: '/productos' },
      { label: 'Importar / Exportar', icon: <FileUpload />, href: '/productos/importar' },
      { label: 'Usuarios', icon: <People />, href: '/usuarios' },
      { label: 'Generar Código Barras', icon: <QrCode />, href: '/generar-codigo' },
      { label: 'Tarjeta Autorización', icon: <CreditCard />, href: '/tarjeta-autorizacion' },
      { label: 'Configuración', icon: <Settings />, href: '/configuracion' },
    ],
  },
  {
    label: 'SISTEMA', icon: <SystemUpdate />,
    items: [
      { label: 'Verificar Actualizaciones', icon: <SystemUpdate />, href: '/actualizaciones' },
      { label: 'Configurar Atajos', icon: <Keyboard />, href: '/configurar-atajos' },
      { label: 'Registro Eventos', icon: <History />, href: '/logs' },
    ],
  },
]

export default function Layout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth()
  const { mode, toggle: toggleTheme } = useThemeMode()
  const pathname = usePathname()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [navFontSize, setNavFontSize] = useState(14)
  useEffect(() => {
    const load = () => { try { const s = localStorage.getItem('app-nav-font-size'); if (s) setNavFontSize(parseInt(s) || 14) } catch {} }
    load()
    window.addEventListener('navfontsizechange', load)
    window.addEventListener('storage', (e) => { if (e.key === 'app-nav-font-size') load() })
    return () => { window.removeEventListener('navfontsizechange', load) }
  }, [])
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)

  if (!user) return <>{children}</>

  const isActive = (href: string) => {
    if (href === '/caja/1') return pathname.startsWith('/caja/')
    return pathname === href || pathname.startsWith(href + '/')
  }

  const drawerContent = (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Brand */}
      <Box sx={{
        display: 'flex', alignItems: 'center', gap: 1.5, px: 2.5, py: 2, minHeight: 64,
        background: (theme) => `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
        color: '#fff',
      }}>
        <Box sx={{ width: 36, height: 36, borderRadius: 1.5, display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: 'rgba(255,255,255,0.2)' }}>
          <Store fontSize="small" />
        </Box>
        <Box>
          <Typography fontWeight={700} fontSize="1rem" lineHeight={1.2}>Registradora</Typography>
          <Typography variant="caption" sx={{ opacity: 0.7 }}>Sistema POS</Typography>
        </Box>
      </Box>

      {/* Menu groups */}
      <Box sx={{ flex: 1, overflow: 'auto', py: 1, px: 1, fontSize: `${navFontSize}px`, '& *': { fontSize: `${navFontSize}px` } }}>
        {menuGroups.map((group) => {
          if (group.adminOnly && user.permisos !== 'admin') return null
          return (
            <Box key={group.label} sx={{ mb: 1 }}>
              <Typography variant="caption" sx={{
                display: 'block', px: 1.5, py: 1, fontWeight: 700, fontSize: `${navFontSize - 4}px`,
                letterSpacing: 1, textTransform: 'uppercase', color: 'text.disabled',
              }}>
                {group.label}
              </Typography>
              <List dense disablePadding>
                {group.items.map((item) => {
                  if (item.adminOnly && user.permisos !== 'admin') return null
                  return (
                    <ListItemButton
                      key={item.href}
                      component={Link}
                      href={item.href}
                      selected={isActive(item.href)}
                      sx={{
                        borderRadius: 2, mb: 0.15, minHeight: 40, px: 1.5, mx: 0.5,
                        '&.Mui-selected': {
                          bgcolor: (theme) => alpha(theme.palette.primary.main, 0.1),
                          '& .MuiListItemIcon-root': { color: 'primary.main' },
                          '& .MuiListItemText-primary': { color: 'primary.main', fontWeight: 700 },
                        },
                        '&:hover': { bgcolor: (theme) => alpha(theme.palette.primary.main, 0.04) },
                      }}
                    >
                      <ListItemIcon sx={{ minWidth: 32, color: isActive(item.href) ? 'primary.main' : 'text.secondary' }}>
                        {item.icon}
                      </ListItemIcon>
                      <ListItemText primary={item.label} primaryTypographyProps={{
                        fontSize: '0.85rem',
                        fontWeight: isActive(item.href) ? 700 : 500,
                      }} />
                    </ListItemButton>
                  )
                })}
              </List>
            </Box>
          )
        })}
      </Box>
    </Box>
  )

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
      {/* Topbar */}
      <AppBar position="fixed" color="inherit" elevation={0}
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
          borderBottom: 1, borderColor: 'divider',
          backdropFilter: 'blur(20px)',
          bgcolor: (theme) => alpha(theme.palette.background.paper, 0.8),
        }}>
        <Toolbar sx={{ px: { xs: 1, sm: 2 } }}>
          <IconButton edge="start" onClick={() => setMobileOpen(true)}
            sx={{ mr: 1, display: { md: 'none' } }}>
            <MenuIcon />
          </IconButton>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Store sx={{ color: 'primary.main' }} />
            <Typography variant="subtitle1" fontWeight={700} sx={{ display: { xs: 'none', sm: 'block' } }}>
              Caja Registradora
            </Typography>
          </Box>
          <Box sx={{ flexGrow: 1 }} />

          <Tooltip title="Volver a UI Clásica">
            <IconButton component="a" href="http://localhost:8000/" target="_blank" size="small" sx={{ mr: 0.5 }}>
              <Typography variant="caption" sx={{ fontWeight: 700, fontSize: 10, opacity: 0.6 }}>Clásica</Typography>
            </IconButton>
          </Tooltip>
          <Tooltip title={mode === 'dark' ? 'Modo claro' : 'Modo oscuro'}>
            <IconButton onClick={toggleTheme} size="small"><DarkMode fontSize="small" /></IconButton>
          </Tooltip>
          <Tooltip title="Menú de usuario">
            <IconButton onClick={(e) => setAnchorEl(e.currentTarget)} size="small" sx={{ ml: 0.5 }}>
              <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main', fontSize: 13, fontWeight: 700 }}>
                {user.username.charAt(0).toUpperCase()}
              </Avatar>
            </IconButton>
          </Tooltip>
          <Menu anchorEl={anchorEl} open={!!anchorEl} onClose={() => setAnchorEl(null)}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            PaperProps={{ sx: { borderRadius: 3, minWidth: 200, mt: 0.5 } }}>
            <Box sx={{ px: 2, py: 1 }}>
              <Typography variant="subtitle2" fontWeight={700}>{user.username}</Typography>
              <Typography variant="caption" color="text.secondary">
                {user.permisos === 'admin' ? 'Administrador' : user.permisos === 'cajero' ? 'Cajero' : 'Bodeguero'}
              </Typography>
            </Box>
            <Divider />
            <MenuItem component={Link} href="/editar-usuario" onClick={() => setAnchorEl(null)}>
              <ListItemIcon><People fontSize="small" /></ListItemIcon> Perfil
            </MenuItem>
            {user.permisos === 'admin' && (
              <MenuItem component={Link} href="/configuracion" onClick={() => setAnchorEl(null)}>
                <ListItemIcon><Settings fontSize="small" /></ListItemIcon> Configuración
              </MenuItem>
            )}
            <Divider />
            <MenuItem onClick={() => { setAnchorEl(null); logout() }}>
              <ListItemIcon><Logout fontSize="small" /></ListItemIcon> Desconectar
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {/* Desktop drawer — siempre visible */}
      <Drawer variant="permanent"
        sx={{
          display: { xs: 'none', md: 'block' },
          width: DRAWER_WIDTH,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            boxSizing: 'border-box',
            borderRight: 1,
            borderColor: 'divider',
            overflow: 'hidden',
          },
        }}>
        {drawerContent}
      </Drawer>

      {/* Mobile drawer — hamburguesa */}
      <Drawer variant="temporary" open={mobileOpen} onClose={() => setMobileOpen(false)}
        sx={{ display: { xs: 'block', md: 'none' }, '& .MuiDrawer-paper': { width: DRAWER_WIDTH } }}>
        {drawerContent}
      </Drawer>

      {/* Main */}
      <Box component="main" sx={{
        flexGrow: 1, p: { xs: 1.5, sm: 2.5, md: 3 }, mt: 8,
        minHeight: 'calc(100vh - 64px)',
        transition: (theme) => theme.transitions.create('margin', { easing: theme.transitions.easing.sharp, duration: theme.transitions.duration.enteringScreen }),
      }}>
        {children}
      </Box>
    </Box>
  )
}
