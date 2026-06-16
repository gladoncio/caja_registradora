'use client'
import { useEffect, useCallback } from 'react'

interface ShortcutMap {
  [key: string]: () => void
}

// Keys that should trigger shortcuts even when typing in inputs
const INPUT_SAFE_KEYS = new Set([
  'F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12',
  'Escape','Enter','Tab','-',
])

export function useKeyboardShortcuts(shortcuts: ShortcutMap, enabled = true) {
  const handler = useCallback(
    (e: KeyboardEvent) => {
      if (!enabled) return

      const key = [
        e.ctrlKey ? 'Ctrl' : '',
        e.shiftKey ? 'Shift' : '',
        e.key.length === 1 ? e.key.toUpperCase() : e.key,
      ]
        .filter(Boolean)
        .join('+')

      // Ctrl shortcuts always work
      if (key.startsWith('Ctrl+') && shortcuts[key]) {
        e.preventDefault()
        shortcuts[key]()
        return
      }

      const target = e.target as HTMLElement
      const inInput = ['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName)

      // In inputs, only allow specific shortcut keys
      if (inInput && !INPUT_SAFE_KEYS.has(key) && !key.startsWith('Ctrl+')) {
        return
      }

      if (shortcuts[key]) {
        e.preventDefault()
        shortcuts[key]()
      }
    },
    [shortcuts, enabled],
  )

  useEffect(() => {
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [handler])
}
