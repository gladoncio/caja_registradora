'use client'
import { useState, useEffect } from 'react'
import {
  Box, Card, CardContent, Grid, Typography, Button, TextField, Fade,
  Dialog, DialogTitle, DialogContent, DialogActions, Chip, CircularProgress,
  Paper, alpha, Alert, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
} from '@mui/material'
import { AccountBalanceWallet, Add, Remove } from '@mui/icons-material'
import { configAPI } from '@/lib/api'
import { Gasto } from '@/types'

export default function CajaDiariaPage() {
  const [caja, setCaja] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [monto, setMonto] = useState('')
  const [retiro, setRetiro] = useState('')
  const [saving, setSaving] = useState(false)
  const [msg, setMsg] = useState<string | null>(null)

  const load = async () => {
    setLoading(true)
    try {
      const r = await configAPI.get()
      setCaja(r.data)
      setMonto(r.data.monto_caja?.toString() || '0')
      setRetiro(r.data.monto_retiro?.toString() || '0')
    } finally { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  const handleSave = async () => {
    setSaving(true)
    try {
      await configAPI.update({ monto_caja: parseFloat(monto), retiro_caja: parseFloat(retiro) })
      setMsg('Caja diaria actualizada')
    } catch { setMsg('Error al guardar') }
    finally { setSaving(false) }
  }

  if (loading) return <Box display="flex" justifyContent="center" py={6}><CircularProgress /></Box>

  return (
    <Fade in timeout={400}>
      <Box>
        <Box display="flex" alignItems="center" gap={1} mb={3}>
          <AccountBalanceWallet color="primary" />
          <Typography variant="h4" fontWeight={700}>Caja Diaria</Typography>
        </Box>

        {msg && <Alert severity="info" sx={{ mb: 2, borderRadius: 2 }} onClose={() => setMsg(null)}>{msg}</Alert>}

        <Card sx={{ borderRadius: 3 }}>
          <CardContent sx={{ p: 3 }}>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <TextField fullWidth label="Monto en caja" type="number" value={monto}
                  onChange={(e) => setMonto(e.target.value)}
                  InputProps={{ startAdornment: <Chip label="$" size="small" sx={{ mr: 1 }} /> }}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField fullWidth label="Retiro acumulado" type="number" value={retiro}
                  onChange={(e) => setRetiro(e.target.value)}
                  InputProps={{ startAdornment: <Chip label="$" size="small" sx={{ mr: 1 }} /> }}
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }} />
              </Grid>
            </Grid>
            <Box display="flex" gap={1} mt={3} justifyContent="flex-end">
              <Button variant="contained" onClick={handleSave} disabled={saving} sx={{ borderRadius: 2 }}>
                {saving ? 'Guardando...' : 'Actualizar Caja Diaria'}
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Fade>
  )
}
