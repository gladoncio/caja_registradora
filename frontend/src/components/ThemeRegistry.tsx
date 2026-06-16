'use client'
import { useState, useEffect, useMemo, createContext, useContext } from 'react'
import { ThemeProvider, createTheme, CssBaseline, GlobalStyles, alpha } from '@mui/material'

type ThemeMode = 'light' | 'dark'

type ThemeCtx = { mode: ThemeMode; toggle: () => void; themeId: string; setThemeId: (id: string) => void }

const ThemeModeContext = createContext<ThemeCtx>({
  mode: 'light', toggle: () => {}, themeId: 'default', setThemeId: () => {},
})

export const useThemeMode = () => useContext(ThemeModeContext)

const typography = {
  fontFamily: '"Inter","PlusJakartaSans","Outfit","Roboto",sans-serif',
  h1: { fontWeight: 800, letterSpacing: -1 },
  h2: { fontWeight: 700, letterSpacing: -0.5 },
  h3: { fontWeight: 700, letterSpacing: -0.3 },
  h4: { fontWeight: 700, letterSpacing: -0.2 },
  h5: { fontWeight: 600 },
  h6: { fontWeight: 600 },
  subtitle1: { fontWeight: 600, letterSpacing: 0.1 },
  subtitle2: { fontWeight: 600, letterSpacing: 0.05 },
  body1: { letterSpacing: 0.01 },
  button: { textTransform: 'none', fontWeight: 600, letterSpacing: 0.02 },
  caption: { fontWeight: 500, letterSpacing: 0.02 },
  overline: { fontWeight: 700, letterSpacing: 0.08, textTransform: 'uppercase' },
}

const baseComponents = {
  MuiCssBaseline: {
    styleOverrides: {
      body: { scrollBehavior: 'smooth', WebkitFontSmoothing: 'antialiased', MozOsxFontSmoothing: 'grayscale' },
    },
  },
  MuiButton: {
    styleOverrides: {
      root: {
        borderRadius: 12, padding: '10px 22px', fontSize: '0.875rem', fontWeight: 600,
        transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
        '&:hover': { transform: 'translateY(-1px)', boxShadow: '0 4px 12px rgba(99,102,241,0.3)' },
        '&:active': { transform: 'translateY(0)' },
      },
      contained: { boxShadow: '0 2px 8px rgba(99,102,241,0.25)' },
      outlined: { borderWidth: 1.5, '&:hover': { borderWidth: 1.5 } },
      sizeSmall: { padding: '6px 14px', fontSize: '0.8125rem' },
      sizeLarge: { padding: '14px 28px', fontSize: '1rem' },
    },
  },
  MuiCard: {
    styleOverrides: {
      root: {
        borderRadius: 20, boxShadow: '0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03)',
        border: '1px solid rgba(0,0,0,0.04)', transition: 'box-shadow 0.2s ease',
        '&:hover': { boxShadow: '0 4px 12px rgba(0,0,0,0.06), 0 2px 4px rgba(0,0,0,0.04)' },
      },
    },
  },
  MuiPaper: {
    styleOverrides: { root: { backgroundImage: 'none' }, elevation1: { boxShadow: '0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03)' } },
  },
  MuiTextField: {
    styleOverrides: {
      root: {
        '& .MuiOutlinedInput-root': {
          borderRadius: 12, transition: 'all 0.2s ease',
          '&:hover': { boxShadow: '0 0 0 2px rgba(99,102,241,0.08)' },
          '&.Mui-focused': { boxShadow: '0 0 0 3px rgba(99,102,241,0.15)' },
        },
      },
    },
  },
  MuiTableHead: {
    styleOverrides: {
      root: {
        '& .MuiTableCell-head': {
          fontWeight: 700, fontSize: '0.6875rem', textTransform: 'uppercase', letterSpacing: 0.08,
          color: '#94a3b8', backgroundColor: 'transparent', borderBottom: '2px solid rgba(0,0,0,0.04)',
          padding: '16px 16px',
        },
      },
    },
  },
  MuiTableCell: {
    styleOverrides: { root: { padding: '14px 16px', borderBottom: '1px solid rgba(0,0,0,0.04)', fontSize: '0.875rem' } },
  },
  MuiChip: {
    styleOverrides: {
      root: { borderRadius: 8, fontWeight: 600, fontSize: '0.75rem' },
      filled: {
        '&.MuiChip-colorPrimary': { background: 'linear-gradient(135deg, #6366f1, #4f46e5)' },
        '&.MuiChip-colorSuccess': { background: 'linear-gradient(135deg, #10b981, #059669)' },
        '&.MuiChip-colorError': { background: 'linear-gradient(135deg, #ef4444, #dc2626)' },
      },
    },
  },
  MuiDrawer: {
    styleOverrides: { paper: { borderRight: '1px solid rgba(0,0,0,0.04)', backgroundImage: 'none' } },
  },
  MuiAppBar: {
    styleOverrides: {
      root: {
        backdropFilter: 'blur(20px) saturate(1.2)', backgroundColor: 'rgba(255,255,255,0.75)',
        boxShadow: '0 1px 3px rgba(0,0,0,0.04)', borderBottom: '1px solid rgba(0,0,0,0.04)',
      },
    },
  },
  MuiTabs: {
    styleOverrides: { indicator: { height: 3, borderRadius: '3px 3px 0 0', background: 'linear-gradient(135deg, #6366f1, #4f46e5)' } },
  },
  MuiTab: {
    styleOverrides: { root: { textTransform: 'none', fontWeight: 600, fontSize: '0.875rem', minHeight: 48, transition: 'color 0.2s ease' } },
  },
  MuiDialog: {
    styleOverrides: { paper: { borderRadius: 24, boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)' } },
  },
  MuiAlert: {
    styleOverrides: {
      root: { borderRadius: 12, fontWeight: 500 },
      standardSuccess: { background: 'linear-gradient(135deg, #ecfdf5, #d1fae5)', color: '#065f46' },
      standardError: { background: 'linear-gradient(135deg, #fef2f2, #fecaca)', color: '#991b1b' },
      standardInfo: { background: 'linear-gradient(135deg, #eff6ff, #bfdbfe)', color: '#1e40af' },
    },
  },
}

const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#6366f1', light: '#a5b4fc', dark: '#4f46e5', contrastText: '#fff' },
    secondary: { main: '#10b981', light: '#6ee7b7', dark: '#059669', contrastText: '#fff' },
    error: { main: '#ef4444', light: '#fca5a5', dark: '#dc2626' },
    warning: { main: '#f59e0b', light: '#fcd34d', dark: '#d97706' },
    info: { main: '#3b82f6', light: '#93c5fd', dark: '#2563eb' },
    success: { main: '#10b981', light: '#6ee7b7', dark: '#059669' },
    background: { default: '#f8fafc', paper: '#ffffff' },
    text: { primary: '#0f172a', secondary: '#64748b' },
    divider: 'rgba(0,0,0,0.06)',
  },
  shape: { borderRadius: 16 },
  typography,
  shadows: [
    'none', '0 1px 2px rgba(0,0,0,0.04)', '0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)',
    '0 4px 6px -1px rgba(0,0,0,0.07), 0 2px 4px -1px rgba(0,0,0,0.04)',
    '0 10px 15px -3px rgba(0,0,0,0.08), 0 4px 6px -2px rgba(0,0,0,0.04)',
    '0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04)',
    '0 25px 50px -12px rgba(0,0,0,0.15)',
    ...Array(18).fill('0 1px 3px rgba(0,0,0,0.06)'),
  ] as any,
  components: baseComponents,
})

const darkTheme = createTheme({
  ...lightTheme,
  palette: {
    mode: 'dark',
    primary: { main: '#818cf8', light: '#a5b4fc', dark: '#6366f1', contrastText: '#fff' },
    secondary: { main: '#34d399', light: '#6ee7b7', dark: '#10b981', contrastText: '#fff' },
    error: { main: '#f87171', light: '#fca5a5', dark: '#ef4444' },
    warning: { main: '#fbbf24', light: '#fcd34d', dark: '#f59e0b' },
    info: { main: '#60a5fa', light: '#93c5fd', dark: '#3b82f6' },
    success: { main: '#34d399', light: '#6ee7b7', dark: '#10b981' },
    background: { default: '#0b1120', paper: '#131c31' },
    text: { primary: '#e2e8f0', secondary: '#94a3b8' },
    divider: 'rgba(255,255,255,0.06)',
  },
  components: {
    ...baseComponents,
    MuiAppBar: {
      styleOverrides: {
        root: {
          backdropFilter: 'blur(20px) saturate(1.2)', backgroundColor: 'rgba(11,17,32,0.8)',
          boxShadow: '0 1px 3px rgba(0,0,0,0.2)', borderBottom: '1px solid rgba(255,255,255,0.04)',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 20, boxShadow: '0 1px 3px rgba(0,0,0,0.2)', border: '1px solid rgba(255,255,255,0.04)',
          backgroundColor: '#131c31',
          '&:hover': { boxShadow: '0 4px 12px rgba(0,0,0,0.3)' },
        },
      },
    },
    MuiPaper: {
      styleOverrides: { root: { backgroundImage: 'none', backgroundColor: '#131c31' } },
    },
    MuiDrawer: {
      styleOverrides: { paper: { borderRight: '1px solid rgba(255,255,255,0.04)', backgroundColor: '#0f1729' } },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 12, transition: 'all 0.2s ease',
            '&:hover': { boxShadow: '0 0 0 2px rgba(129,140,248,0.12)' },
            '&.Mui-focused': { boxShadow: '0 0 0 3px rgba(129,140,248,0.2)' },
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: { '&:hover': { transform: 'translateY(-1px)' } },
        contained: { boxShadow: '0 2px 8px rgba(129,140,248,0.3)' },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: { borderRadius: 12, fontWeight: 500 },
        standardSuccess: { background: 'linear-gradient(135deg, rgba(16,185,129,0.15), rgba(5,150,105,0.1))', color: '#6ee7b7' },
        standardError: { background: 'linear-gradient(135deg, rgba(239,68,68,0.15), rgba(220,38,38,0.1))', color: '#fca5a5' },
        standardInfo: { background: 'linear-gradient(135deg, rgba(59,130,246,0.15), rgba(37,99,235,0.1))', color: '#93c5fd' },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: { borderRadius: 8, fontWeight: 600 },
        filled: {
          '&.MuiChip-colorPrimary': { background: 'linear-gradient(135deg, #6366f1, #4f46e5)' },
          '&.MuiChip-colorSuccess': { background: 'linear-gradient(135deg, #10b981, #059669)' },
          '&.MuiChip-colorError': { background: 'linear-gradient(135deg, #ef4444, #dc2626)' },
        },
      },
    },
    MuiTableHead: {
      styleOverrides: {
        root: {
          '& .MuiTableCell-head': { color: '#64748b', borderBottom: '2px solid rgba(255,255,255,0.04)' },
        },
      },
    },
    MuiTableCell: {
      styleOverrides: { root: { borderBottom: '1px solid rgba(255,255,255,0.04)', color: '#e2e8f0' } },
    },
  },
})

function applyThemeColors(theme: ReturnType<typeof createTheme>, id: string, m: ThemeMode) {
  try {
    const raw = localStorage.getItem('app-themes')
    if (!raw) return theme
    const themes = JSON.parse(raw)
    const tc = themes?.[id]?.[m]
    if (tc && typeof tc.primary === 'string' && typeof tc.secondary === 'string' && tc.primary.startsWith('#')) {
      theme.palette.primary.main = tc.primary
      theme.palette.secondary.main = tc.secondary
    }
  } catch {}
  return theme
}

export default function ThemeRegistry({ children }: { children: React.ReactNode }) {
  const [mode, setMode] = useState<ThemeMode>('light')
  const [themeId, setThemeIdState] = useState('default')
  const [mounted, setMounted] = useState(false)
  const [customTheme, setCustomTheme] = useState<ReturnType<typeof createTheme> | null>(null)

  useEffect(() => {
    const saved = localStorage.getItem('theme-mode') as ThemeMode | null
    if (saved) setMode(saved)
    const t = localStorage.getItem('app-theme-id') || 'default'
    setThemeIdState(t)
    setMounted(true)
  }, [])

  const toggle = () => {
    setMode((prev) => {
      const next = prev === 'light' ? 'dark' : 'light'
      localStorage.setItem('theme-mode', next)
      return next
    })
  }

  const setThemeId = (id: string) => {
    setThemeIdState(id)
    localStorage.setItem('app-theme-id', id)
  }

  const theme = useMemo(() => {
    const base = mode === 'dark' ? darkTheme : lightTheme
    const raw = typeof window !== 'undefined' ? localStorage.getItem('app-themes') : null
    if (!raw) return base
    try {
      const themes = JSON.parse(raw)
      const tc = themes?.[themeId]?.[mode]
      if (tc && typeof tc.primary === 'string' && typeof tc.secondary === 'string' && tc.primary.startsWith('#')) {
        const merged = createTheme(base)
        merged.palette.primary.main = tc.primary
        merged.palette.secondary.main = tc.secondary
        return merged
      }
    } catch {}
    return base
  }, [mode, themeId])

  if (!mounted) return <>{children}</>

  return (
    <ThemeModeContext.Provider value={{ mode, toggle, themeId, setThemeId }}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <GlobalStyles styles={{
          '*, *::before, *::after': {
            transition: 'background-color 0.3s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.2s ease, color 0.2s ease, box-shadow 0.2s ease',
          },
          '::selection': { backgroundColor: alpha(theme.palette.primary.main, 0.2), color: theme.palette.text.primary },
          '::-webkit-scrollbar': { width: 6, height: 6 },
          '::-webkit-scrollbar-track': { background: 'transparent' },
          '::-webkit-scrollbar-thumb': {
            background: theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)',
            borderRadius: 3,
            '&:hover': { background: theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.12)' },
          },
          '@keyframes fadeIn': { from: { opacity: 0, transform: 'translateY(8px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
          '@keyframes slideUp': { from: { opacity: 0, transform: 'translateY(12px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
          '@keyframes scaleIn': { from: { opacity: 0, transform: 'scale(0.95)' }, to: { opacity: 1, transform: 'scale(1)' } },
          '.animate-fadeIn': { animation: 'fadeIn 0.3s cubic-bezier(0.4, 0, 0.2, 1)' },
          '.animate-slideUp': { animation: 'slideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1)' },
          '.animate-scaleIn': { animation: 'scaleIn 0.2s cubic-bezier(0.4, 0, 0.2, 1)' },
        }} />
        {children}
      </ThemeProvider>
    </ThemeModeContext.Provider>
  )
}
