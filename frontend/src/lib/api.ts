import axios from 'axios'

const hostname = typeof window !== 'undefined' ? window.location.hostname : 'localhost'
const API_BASE = `http://${hostname}:8000/api`

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refresh = localStorage.getItem('refresh_token')
      if (refresh) {
        try {
          const res = await axios.post(`${API_BASE}/token/refresh/`, { refresh })
          const { access } = res.data
          localStorage.setItem('access_token', access)
          originalRequest.headers.Authorization = `Bearer ${access}`
          return api(originalRequest)
        } catch {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

export default api

export const authAPI = {
  login: (username: string, password: string) =>
    api.post('/token/', { username, password }),
  me: () => api.get('/me/'),
}

export const productosAPI = {
  list: (params?: any) => api.get('/productos/', { params }),
  get: (id: number) => api.get(`/productos/${id}/`),
  create: (data: any) => api.post('/productos/', data),
  update: (id: number, data: any) => api.put(`/productos/${id}/`, data),
  delete: (id: number) => api.delete(`/productos/${id}/`),
  search: (q: string) => api.get('/productos/busqueda/', { params: { q } }),
  rapidos: () => api.get('/productos/rapidos/'),
  agregarRapido: (id: number) => api.post(`/productos/${id}/agregar_rapido/`),
  eliminarRapido: (id: number) => api.delete(`/productos/${id}/eliminar_rapido/`),
  configRapido: (data: any) => api.put('/productos/config_rapido/', data),
}

export const carritoAPI = {
  list: (carritoNumero?: number) =>
    api.get('/carrito/', { params: carritoNumero ? { carrito_numero: carritoNumero } : {} }),
  agregar: (productoId: number, cantidad: number, carritoNumero: number, extra?: { valor?: number; gramaje?: number }) =>
    api.post('/carrito/agregar/', { producto_id: productoId, cantidad, carrito_numero: carritoNumero, ...extra }),
  delete: (id: number) => api.delete(`/carrito/${id}/`),
  vaciar: (carritoNumero: number) => api.post('/carrito/vaciar/', { carrito_numero: carritoNumero }),
  total: (carritoNumero: number) => api.get('/carrito/total/', { params: { carrito_numero: carritoNumero } }),
  numeros: () => api.get('/carrito/numeros/'),
  nuevo: () => api.post('/carrito/nuevo/'),
}

export const ventasAPI = {
  list: (params?: any) => api.get('/ventas/', { params }),
  get: (id: number) => api.get(`/ventas/${id}/`),
  generar: (data: any) => api.post('/ventas/generar/', data),
  eliminar: (id: number, clave: string) =>
    api.delete(`/ventas/${id}/eliminar/`, { data: { clave_anulacion: clave } }),
  respaldo: () => api.get('/ventas/respaldo/'),
}

export const configAPI = {
  get: () => api.get('/configuracion/'),
  update: (data: any) => api.put('/configuracion/', data),
}

export const reportesAPI = {
  general: () => api.get('/reportes/general/'),
  cuadrar: (data: any) => api.post('/reportes/cuadrar/', data),
}

export const gastosAPI = {
  list: () => api.get('/gastos/'),
  create: (data: any) => api.post('/gastos/', data),
}

export const impresoraAPI = {
  probar: () => api.get('/impresora/probar/'),
  estado: () => api.get('/impresora/estado/'),
}

export const autorizacionAPI = {
  verificarClave: (clave: string) => api.post('/autorizar/', { clave }),
  abrirCajon: (clave: string) => api.post('/caja-diaria/abrir/', { clave }),
}

export const metodosPagoAPI = {
  list: () => api.get('/metodos-pago/'),
}
