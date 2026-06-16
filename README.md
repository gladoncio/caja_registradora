# Caja Registradora — POS System

Sistema POS (Punto de Venta) completo para pequeños negocios. Consta de dos interfaces:

- **UI Clásica** (Django Templates) — `http://localhost:8000`
- **UI Moderna** (Next.js + MUI) — `http://localhost:3005`

## Stack Tecnológico

| Componente | Tecnología |
|------------|------------|
| Backend | Django 4.2 + Django REST Framework |
| Base de datos | PostgreSQL 16 |
| Frontend Clásico | Django Templates + Bootstrap 4 + SB Admin 2 |
| Frontend Moderno | Next.js 14 + Material UI 5 + Tailwind CSS |
| Autenticación | JWT (SimpleJWT) + Sesiones Django |
| Contenedores | Docker + Docker Compose |

## Arquitectura

```
app/                    ← Backend Django
├── api/                ← API REST (serializers, viewsets, urls)
├── core/               ← Modelos, lógica de negocio, templates clásicos
└── cash_register/      ← Configuración Django (settings, root urls)

frontend/               ← Frontend Next.js
├── src/
│   ├── app/            ← Páginas (App Router)
│   ├── components/     ← Componentes reutilizables
│   ├── contexts/       ← Contextos (Auth)
│   └── lib/            ← Utilidades (API client, shortcuts, themes)
└── package.json

docker-compose.yml      ← 4 servicios: caja, frontend, db, adminer
```

## Funcionalidades

### POS / Caja
- 8 cajas simultáneas con tabs (F1-F8)
- Búsqueda de productos por código de barras o nombre
- Productos rápidos con atajos de teclado (presiona `-` + número)
- Tipos de producto: unidad, gramaje, valor personalizado
- Métodos de pago: Efectivo, Efectivo Justo, Transferencia, Débito
- Pagos divididos (efectivo + otro método)
- Cálculo automático de vuelto
- Apertura de cajón con autorización por clave
- Impresión de tickets (USB o IP)

### Atajos de Teclado
| Tecla | Acción |
|-------|--------|
| F1-F8 | Cambiar de caja |
| F9 | Nueva caja |
| F10 | Cobrar |
| Ctrl+D | Abrir cajón |
| `-` + número | Producto rápido |

Configurables en: **Sistema → Configurar Atajos**

### Productos
- CRUD completo con diálogo visual
- Paginación, filtros (departamento, tipo) y orden (nombre, precio, costo, fecha)
- Asignación de productos rápidos (máx 10) desde la misma página
- Importar/Exportar Excel
- Sugerencia de precio basada en costo + margen
- Cálculo de IVA automático

### Ventas
- Listado con filtros por fecha/hora
- Detalle de venta en panel lateral
- Anulación con clave de autorización
- Ventas de respaldo (anuladas)

### Reportes
- Reporte general con totales por método de pago
- Ventas por departamento
- Calendario de cierres mensuales
- Cuadre de caja (conteo de billetes/monedas)
- Detalle por día específico

### Administración
- Gestión de usuarios (roles: admin, cajero, bodeguero)
- Configuración del sistema
- Apariencia: temas predefinidos (Default, Océano, Atardecer, Bosque, Medianoche)
- Tamaño de fuente (contenido y menú lateral)
- Colores personalizados (primario, secundario)
- Colores de cajas (tabs)

### Sistema
- Verificar actualizaciones (GitHub Releases)
- Registro de eventos (ventas, gastos, cierres)
- Atajos de teclado configurables

## Temas

| Tema | Primario | Secundario |
|------|----------|------------|
| Default | Indigo #6366f1 | Emerald #10b981 |
| Océano | Azul #0284c7 | Teal #0d9488 |
| Atardecer | Naranja #ea580c | Rosa #d946ef |
| Bosque | Verde #16a34a | Lima #65a30d |
| Medianoche | Púrpura #7c3aed | Cian #0891b2 |

## Modelos de Datos

Los principales modelos son:
- `Usuario` — Usuarios con roles y clave de anulación
- `Producto` — Productos con precio, costo, tipo de venta
- `ProductoRapido` — Productos de acceso rápido con tecla y color
- `CarritoItem` — Items en carrito de compras
- `Venta` / `VentaProducto` / `FormaPago` — Ventas realizadas
- `Configuracion` — Configuración global del sistema
- `CajaDiaria` / `RegistroTransaccion` — Gestión de caja
- `GastoCaja` — Gastos registrados
- `VentaRespaldo` — Ventas anuladas (backup)

## Despliegue

```bash
# Iniciar todos los servicios
docker-compose up -d

# Reconstruir frontend
docker-compose build frontend

# Ver logs
docker-compose logs -f

# Generar datos de prueba
docker exec caja_registradora-caja-1 python /app/seed_data.py
```

## URLs

| Servicio | URL |
|----------|-----|
| UI Clásica | http://localhost:8000 |
| UI Moderna | http://localhost:3005 |
| API REST | http://localhost:8000/api/ |
| Adminer (DB) | http://localhost:8080 |

**Login:** admin / 123
