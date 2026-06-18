'use client'
import { useState, useEffect } from 'react'
import {
  Box, Card, CardContent, Typography, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, CircularProgress, Fade, Chip,
} from '@mui/material'
import { Receipt } from '@mui/icons-material'
import { ventasAPI } from '@/lib/api'
import { formatMoney, formatNumber } from '@/lib/format'

export default function VentasRespaldoPage() {
  const [ventas, setVentas] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    ventasAPI.respaldo().then((r) => setVentas(r.data.results || r.data)).finally(() => setLoading(false))
  }, [])

  return (
    <Fade in timeout={300}>
      <Box>
        <Typography variant="h4" fontWeight={700} mb={3}>Anulaciones</Typography>
        <Card sx={{ borderRadius: 3 }}>
          <CardContent>
            {loading ? <Box textAlign="center" py={6}><CircularProgress /></Box> : (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell># Original</TableCell>
                      <TableCell>Fecha</TableCell>
                      <TableCell>Anulación</TableCell>
                      <TableCell>Total</TableCell>
                      <TableCell>Usuario</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {ventas.map((v) => (
                      <TableRow key={v.id} hover>
                        <TableCell><Chip label={`#${v.venta_original_id}`} size="small" /></TableCell>
                        <TableCell>{new Date(v.fecha_hora).toLocaleString('es-CL')}</TableCell>
                        <TableCell>{new Date(v.fecha_anulacion).toLocaleString('es-CL')}</TableCell>
                        <TableCell><Typography fontWeight={700}>{formatMoney(v.total)}</Typography></TableCell>
                        <TableCell>{v.usuario_username}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </CardContent>
        </Card>
      </Box>
    </Fade>
  )
}
