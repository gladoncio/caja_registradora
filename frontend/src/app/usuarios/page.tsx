'use client'
import { useState, useEffect } from 'react'
import {
  Box, Card, CardContent, Typography, Button, Table, TableBody,
  TableCell, TableContainer, TableHead, TableRow, Dialog, DialogTitle,
  DialogContent, DialogActions, TextField, Select, MenuItem, FormControl,
  InputLabel, Chip, IconButton, Tooltip, CircularProgress, Fade, Switch,
} from '@mui/material'
import { People, Add, Edit } from '@mui/icons-material'
import api from '@/lib/api'
import { Usuario } from '@/types'

type Permisos = 'cajero' | 'admin' | 'bodeguero'

const initialForm = {
  username: '',
  password: '',
  email: '',
  permisos: 'cajero' as Permisos,
  rut: '',
  clave_anulacion: '',
}

export default function UsuariosPage() {
  const [users, setUsers] = useState<Usuario[]>([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editing, setEditing] = useState<Usuario | null>(null)
  const [form, setForm] = useState(initialForm)
  const [saving, setSaving] = useState(false)

  const loadUsers = async () => {
    try {
      const res = await api.get('/usuarios/')
      setUsers(res.data.results || res.data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadUsers() }, [])

  const openCreate = () => {
    setEditing(null)
    setForm(initialForm)
    setDialogOpen(true)
  }

  const openEdit = (user: Usuario) => {
    setEditing(user)
    setForm({
      username: user.username,
      password: '',
      email: user.email,
      permisos: user.permisos,
      rut: user.rut,
      clave_anulacion: user.clave_anulacion,
    })
    setDialogOpen(true)
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      if (editing) {
        const { password: _, ...payload } = form
        await api.put(`/usuarios/${editing.id}/`, payload)
      } else {
        await api.post('/usuarios/', form)
      }
      setDialogOpen(false)
      await loadUsers()
    } finally {
      setSaving(false)
    }
  }

  const toggleActive = async (user: Usuario) => {
    await api.patch(`/usuarios/${user.id}/`, { is_active: !user.is_active })
    await loadUsers()
  }

  if (loading) return <Box display="flex" justifyContent="center" py={6}><CircularProgress /></Box>

  return (
    <Fade in timeout={400}>
      <Box>
        <Box display="flex" alignItems="center" gap={1} mb={3}>
          <People color="primary" />
          <Typography variant="h4" fontWeight={700} sx={{ flexGrow: 1 }}>Usuarios</Typography>
          <Button variant="contained" startIcon={<Add />} onClick={openCreate} sx={{ borderRadius: 2 }}>
            Nuevo Usuario
          </Button>
        </Box>

        <Card sx={{ borderRadius: 3 }}>
          <CardContent sx={{ p: 0 }}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 700 }}>Usuario</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Email</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Permisos</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>RUT</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Activo</TableCell>
                    <TableCell sx={{ fontWeight: 700 }} align="right">Acciones</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {users.map((user) => (
                    <TableRow key={user.id} hover>
                      <TableCell>
                        <Typography fontWeight={600}>{user.username}</Typography>
                      </TableCell>
                      <TableCell>{user.email}</TableCell>
                      <TableCell>
                        <Chip
                          label={user.permisos}
                          size="small"
                          color={user.permisos === 'admin' ? 'error' : user.permisos === 'cajero' ? 'primary' : 'warning'}
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell>{user.rut}</TableCell>
                      <TableCell>
                        <Switch
                          checked={user.is_active}
                          onChange={() => toggleActive(user)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="right">
                        <Tooltip title="Editar">
                          <IconButton size="small" onClick={() => openEdit(user)}>
                            <Edit fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                  {users.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={6} align="center">
                        <Typography color="text.secondary" py={4}>No hay usuarios registrados</Typography>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>

        <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>{editing ? 'Editar Usuario' : 'Nuevo Usuario'}</DialogTitle>
          <DialogContent>
            <Box display="flex" flexDirection="column" gap={2} pt={1}>
              <TextField
                label="Nombre de usuario"
                value={form.username}
                onChange={(e) => setForm({ ...form, username: e.target.value })}
                fullWidth size="small"
                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
              />
              {!editing && (
                <TextField
                  label="Contraseña"
                  type="password"
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                  fullWidth size="small"
                  sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
                />
              )}
              <TextField
                label="Email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                fullWidth size="small"
                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
              />
              <FormControl fullWidth size="small">
                <InputLabel>Permisos</InputLabel>
                <Select
                  value={form.permisos}
                  label="Permisos"
                  onChange={(e) => setForm({ ...form, permisos: e.target.value as Permisos })}
                  sx={{ borderRadius: 2 }}
                >
                  <MenuItem value="cajero">Cajero</MenuItem>
                  <MenuItem value="admin">Admin</MenuItem>
                  <MenuItem value="bodeguero">Bodeguero</MenuItem>
                </Select>
              </FormControl>
              <TextField
                label="RUT"
                value={form.rut}
                onChange={(e) => setForm({ ...form, rut: e.target.value })}
                fullWidth size="small"
                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
              />
              <TextField
                label="Clave de anulación"
                value={form.clave_anulacion}
                onChange={(e) => setForm({ ...form, clave_anulacion: e.target.value })}
                fullWidth size="small"
                sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)} sx={{ borderRadius: 2 }}>Cancelar</Button>
            <Button variant="contained" onClick={handleSave} disabled={saving} sx={{ borderRadius: 2 }}>
              {saving ? 'Guardando...' : 'Guardar'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Fade>
  )
}
