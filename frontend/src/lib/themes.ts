export interface AppTheme {
  id: string
  name: string
  light: { primary: string; secondary: string }
  dark: { primary: string; secondary: string }
}

export const THEMES: AppTheme[] = [
  {
    id: 'default', name: 'Default',
    light: { primary: '#6366f1', secondary: '#10b981' },
    dark: { primary: '#818cf8', secondary: '#34d399' },
  },
  {
    id: 'ocean', name: 'Océano',
    light: { primary: '#0284c7', secondary: '#0d9488' },
    dark: { primary: '#38bdf8', secondary: '#2dd4bf' },
  },
  {
    id: 'sunset', name: 'Atardecer',
    light: { primary: '#ea580c', secondary: '#d946ef' },
    dark: { primary: '#fb923c', secondary: '#e879f9' },
  },
  {
    id: 'forest', name: 'Bosque',
    light: { primary: '#16a34a', secondary: '#65a30d' },
    dark: { primary: '#4ade80', secondary: '#a3e635' },
  },
  {
    id: 'midnight', name: 'Medianoche',
    light: { primary: '#7c3aed', secondary: '#0891b2' },
    dark: { primary: '#a78bfa', secondary: '#22d3ee' },
  },
]

export function getThemeColors(themeId: string, mode: 'light' | 'dark') {
  const theme = THEMES.find(t => t.id === themeId) || THEMES[0]
  return mode === 'light' ? theme.light : theme.dark
}
