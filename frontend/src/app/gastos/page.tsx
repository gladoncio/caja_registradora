'use client'
import { useState, useEffect } from 'react'
import {
  Box, Card, CardContent, Typography, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Button, CircularProgress,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField,
} from '@mui/material'
import { Add } from '@mui/icons-material'
import { gastosAPI } from '@/lib/api'
import { Gasto } from '@/types'

export default function GastosPage() {
  const [gastos, setGastos] = useState<Gasto[]>([])
  const [loading, setLoading] = useState(true)
  const [dialog, setDialog] = useState(false)
  const [monto, setMonto] = useState('')
  const [descripcion, setDescripcion] = useState('')

  const loadGastos = async () => {
    setLoading(true)
    try {
      const res = await gastosAPI.list()
      setGastos(res.data.results || res.data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadGastos() }, [])

  const handleAdd = async () => {
    try {
      await gastosAPI.create({ monto, descripcion })
      setDialog(false)
      setMonto('')
      setDescripcion('')
      loadGastos()
    } catch {
      alert('Error al registrar gasto')
    }
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h4">Gastos</Typography>
        <Button variant="contained" startIcon={<Add />} onClick={() => setDialog(true)}>
          Nuevo Gasto
        </Button>
      </Box>

      <Card>
        <CardContent>
          {loading ? (
            <Box display="flex" justifyContent="center" p={4}><CircularProgress /></Box>
          ) : (
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Fecha</TableCell>
                    <TableCell>Descripción</TableCell>
                    <TableCell>Monto</TableCell>
                    <TableCell>Usuario</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {gastos.map((g) => (
                    <TableRow key={g.id}>
                      <TableCell>{new Date(g.fecha_hora).toLocaleString('es-CL')}</TableCell>
                      <TableCell>{g.descripcion}</TableCell>
                      <TableCell>${g.monto}</TableCell>
                      <TableCell>{g.usuario_username}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      <Dialog open={dialog} onClose={() => setDialog(false)}>
        <DialogTitle>Nuevo Gasto</DialogTitle>
        <DialogContent>
          <TextField fullWidth label="Monto" type="number" margin="normal"
            value={monto} onChange={(e) => setMonto(e.target.value)} />
          <TextField fullWidth label="Descripción" margin="normal" multiline rows={2}
            value={descripcion} onChange={(e) => setDescripcion(e.target.value)} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialog(false)}>Cancelar</Button>
          <Button variant="contained" onClick={handleAdd}>Guardar</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
