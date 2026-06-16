export interface Usuario {
  id: number
  username: string
  email: string
  rut: string
  permisos: 'cajero' | 'admin' | 'bodeguero'
  ventas_config: 'pruebas' | 'normales'
  foto_perfil: string | null
  clave_anulacion: string
  is_active: boolean
}

export interface Departamento {
  id: number
  nombre: string
}

export interface Marca {
  id: number
  nombre: string
}

export interface Stock {
  producto: number
  cantidad: number
  gramaje: number
}

export interface Producto {
  id_producto: number
  nombre: string
  valor_costo: string
  precio: string
  codigo_barras: string
  gramaje: string | null
  foto: string | null
  descripcion: string | null
  departamento: number | null
  departamento_nombre: string | null
  marca: number | null
  marca_nombre: string | null
  tipo_gramaje: 'kg' | 'g' | 'Ml' | 'L' | null
  tipo_venta: 'unidad' | 'gramaje' | 'valor'
  stock: Stock | null
}

export interface ProductoSimple {
  id_producto: number
  nombre: string
  precio: string
  codigo_barras: string
  tipo_venta: 'unidad' | 'gramaje' | 'valor'
}

export interface ProductoRapido {
  id: number
  producto: ProductoSimple
  tecla: string | null
  color: string
  orden: number
}

export interface CarritoItem {
  id: number
  usuario: number
  carrito_numero: number
  producto: ProductoSimple
  cantidad: number
  gramaje: number | null
  valor: string | null
  fecha_agregado: string
  subtotal: number
}

export interface Configuracion {
  id: number
  decimales: number
  clave_anulacion: string
  idioma: string
  imprimir: 'no' | 'con_corte' | 'sin_corte'
  separador: '1' | '2'
  tipo_venta: '1' | '2' | '3'
  porcentaje_iva: string
  tamano_letra: number
  tipo_impresora: 'usb' | 'ip'
  ip_impresora: string
  puerto_impresora: number
  tipo_autorizacion: 'cualquier' | 'propio'
}

export interface VentaProducto {
  producto: number
  producto_nombre: string
  cantidad: number | null
  gramaje: number | null
  subtotal: string
}

export interface FormaPago {
  tipo_pago: string
  monto: string
}

export interface Venta {
  id: number
  fecha_hora: string
  total: string
  vuelto: string
  usuario: number
  usuario_username: string
  productos: VentaProducto[]
  formas_pago: FormaPago[]
}

export interface InformeGeneral {
  total_ventas: number
  monto_efectivo: number
  monto_debito: number
  monto_transferencia: number
  monto_credito: number
  monto_retiro: number
  monto_caja: number
  total_gastos: number
  caja_que_deberia: number
  ventas_por_departamento: { producto__departamento__nombre: string; total: number }[]
  decimales: number
}

export interface Gasto {
  id: number
  monto: string
  descripcion: string
  fecha_hora: string
  usuario: number
  usuario_username: string
}
