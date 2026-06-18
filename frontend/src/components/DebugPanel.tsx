'use client'
import { useState, useEffect, useCallback } from 'react'
import {
  Box, Paper, Typography, IconButton, Chip, alpha, Fade, Tooltip,
} from '@mui/material'
import { BugReport, Close, Refresh } from '@mui/icons-material'

interface LogEntry {
  id: number
  method: string
  url: string
  status?: number
  duration?: number
  payload?: any
  response?: any
  error?: string
  time: string
}

let logs: LogEntry[] = []
let logId = 0
let listeners: (() => void)[] = []

function addLog(entry: Omit<LogEntry, 'id' | 'time'>) {
  logs = [{ ...entry, id: ++logId, time: new Date().toLocaleTimeString() }, ...logs].slice(0, 200)
  listeners.forEach(fn => fn())
}

export function debugLog(method: string, url: string, payload?: any) {
  addLog({ method, url, payload })
}

export function debugResponse(id: number, status: number, response?: any, duration?: number) {
  logs = logs.map(l => l.id === id ? { ...l, status, response, duration } : l)
  listeners.forEach(fn => fn())
}

export function debugError(id: number, error: string) {
  logs = logs.map(l => l.id === id ? { ...l, error } : l)
  listeners.forEach(fn => fn())
}

export function installDebugInterceptor(axiosInstance: any) {
  axiosInstance.interceptors.request.use((config: any) => {
    const id = ++logId
    const entry: LogEntry = {
      id, method: config.method?.toUpperCase() || '?', url: config.url || '?',
      payload: config.data, time: new Date().toLocaleTimeString(),
    }
    logs = [entry, ...logs].slice(0, 200)
    listeners.forEach(fn => fn())
    const start = Date.now()
    config._debugId = id
    config._debugStart = start
    return config
  })

  axiosInstance.interceptors.response.use(
    (response: any) => {
      const id = response.config?._debugId
      const start = response.config?._debugStart
      if (id) {
        logs = logs.map(l => l.id === id ? {
          ...l, status: response.status, response: response.data,
          duration: start ? Date.now() - start : undefined,
        } : l)
        listeners.forEach(fn => fn())
      }
      return response
    },
    (error: any) => {
      const id = error.config?._debugId
      const start = error.config?._debugStart
      if (id) {
        logs = logs.map(l => l.id === id ? {
          ...l, status: error.response?.status, error: error.message,
          duration: start ? Date.now() - start : undefined,
        } : l)
        listeners.forEach(fn => fn())
      }
      return Promise.reject(error)
    }
  )
}

export default function DebugPanel({ api }: { api: any }) {
  const [open, setOpen] = useState(false)
  const [entries, setEntries] = useState<LogEntry[]>([])

  useEffect(() => {
    installDebugInterceptor(api)
  }, [api])

  useEffect(() => {
    const update = () => setEntries([...logs])
    listeners.push(update)
    return () => { listeners = listeners.filter(fn => fn !== update) }
  }, [])

  return (
    <>
      <Tooltip title="Debug (Ctrl+Shift+D)">
        <IconButton onClick={() => setOpen(true)}
          sx={{
            position: 'fixed', bottom: 16, right: 16, zIndex: 99998,
            bgcolor: alpha('#000', 0.7), color: '#fff',
            '&:hover': { bgcolor: '#000' },
            width: 40, height: 40,
          }}>
          <BugReport fontSize="small" />
        </IconButton>
      </Tooltip>

      {open && (
        <Fade in>
          <Paper sx={{
            position: 'fixed', bottom: 64, right: 16, zIndex: 99998,
            width: 480, maxHeight: 500, overflow: 'auto',
            borderRadius: 3, boxShadow: 24, border: 1, borderColor: 'divider',
            bgcolor: '#1a1a2e', color: '#e0e0e0',
          }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ p: 1.5, borderBottom: 1, borderColor: alpha('#fff', 0.1), position: 'sticky', top: 0, bgcolor: '#1a1a2e', zIndex: 1 }}>
              <Box display="flex" alignItems="center" gap={1}>
                <BugReport sx={{ fontSize: 18, color: '#6366f1' }} />
                <Typography fontWeight={700} sx={{ fontSize: '0.85rem' }}>Debug</Typography>
                <Chip label={entries.length} size="small" sx={{ height: 18, fontSize: 10, bgcolor: alpha('#6366f1', 0.3), color: '#fff' }} />
              </Box>
              <Box display="flex" gap={0.5}>
                <IconButton size="small" onClick={() => { logs = []; setEntries([]) }} sx={{ color: alpha('#fff', 0.5) }}><Refresh fontSize="small" /></IconButton>
                <IconButton size="small" onClick={() => setOpen(false)} sx={{ color: alpha('#fff', 0.5) }}><Close fontSize="small" /></IconButton>
              </Box>
            </Box>

            {entries.length === 0 && (
              <Box textAlign="center" py={4}><Typography sx={{ fontSize: '0.75rem', color: alpha('#fff', 0.3) }}>Sin actividad</Typography></Box>
            )}

            {entries.map(entry => (
              <Box key={entry.id} sx={{
                p: 1, borderBottom: 1, borderColor: alpha('#fff', 0.05),
                '&:hover': { bgcolor: alpha('#fff', 0.03) },
              }}>
                <Box display="flex" alignItems="center" gap={1} mb={0.3}>
                  <Chip label={entry.method} size="small" sx={{
                    height: 16, fontSize: 8, fontWeight: 700,
                    bgcolor: entry.method === 'GET' ? alpha('#22c55e', 0.2) : entry.method === 'POST' ? alpha('#6366f1', 0.2) : alpha('#f59e0b', 0.2),
                    color: entry.method === 'GET' ? '#22c55e' : entry.method === 'POST' ? '#6366f1' : '#f59e0b',
                  }} />
                  <Typography sx={{ fontSize: '0.7rem', color: alpha('#fff', 0.7), flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {entry.url}
                  </Typography>
                  {entry.status && (
                    <Chip label={entry.status} size="small" sx={{
                      height: 16, fontSize: 8, fontWeight: 700,
                      bgcolor: entry.status < 300 ? alpha('#22c55e', 0.2) : alpha('#ef4444', 0.2),
                      color: entry.status < 300 ? '#22c55e' : '#ef4444',
                    }} />
                  )}
                  {entry.duration !== undefined && (
                    <Typography sx={{ fontSize: '0.65rem', color: alpha('#fff', 0.3), minWidth: 30, textAlign: 'right' }}>
                      {entry.duration}ms
                    </Typography>
                  )}
                </Box>
                {entry.error && (
                  <Typography sx={{ fontSize: '0.7rem', color: '#ef4444' }}>{entry.error}</Typography>
                )}
                <Typography sx={{ fontSize: '0.6rem', color: alpha('#fff', 0.2) }}>{entry.time}</Typography>
              </Box>
            ))}
          </Paper>
        </Fade>
      )}
    </>
  )
}
