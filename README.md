# Catalyst - Sistema de Gestión Multi-Tenant

Plataforma de e-commerce empresarial con arquitectura multi-tenant para gestionar productos, inventarios, pedidos, sucursales y proveedores de forma centralizada.

## Características Principales

### 🏢 Multi-Tenant
- Aislamiento completo de datos por empresa
- Cada empresa gestiona su propio catálogo y operaciones
- Control de acceso basado en roles

### 📦 Gestión de Productos
- CRUD completo de productos con SKU único
- Gestión de categorías y estados
- Control de precios y promociones

### 🏪 Inventario y Sucursales
- Múltiples sucursales por empresa
- Inventario distribuido por ubicación
- Seguimiento de stock en tiempo real

### 📋 Órdenes de Compra
- Creación y seguimiento de compras
- Integración con proveedores
- Estados de pedido automatizados

### 👥 Gestión de Usuarios
- Autenticación con JWT
- Roles: Admin, Gerente, Empleado
- Permisos granulares por recurso

### 🤝 Proveedores
- Base de datos de proveedores
- Órdenes de compra automáticas
- Historial de transacciones

## Stack Tecnológico

- **Backend**: Django 5.2.8 + Django REST Framework 3.14.0
- **Base de datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Autenticación**: JWT (djangorestframework-simplejwt)
- **Frontend**: Vanilla JavaScript con CSS Grid/Flexbox
- **Python**: 3.13

## Estructura del Proyecto

```
catalyst/
├── apps/
│   ├── catalyst_app/          # App principal
│   │   ├── models/            # Modelos de datos
│   │   ├── serializers/       # Serializadores DRF
│   │   └── views/             # Vistas por módulo
│   └── subscriptions/         # App de suscripciones
├── ui/                        # Interfaz web
│   ├── templates/             # HTML
│   ├── static/               # CSS, JS, imágenes
├── catalyst/                  # Configuración Django
└── manage.py                  # CLI Django
```

## Instalación

```bash
# Clonar o descargar el proyecto
cd catalyst

# Crear entorno virtual
python -m venv env

# Activar entorno
.\env\Scripts\Activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones
python manage.py migrate

# Iniciar servidor
python manage.py runserver
```

## Uso

1. **Acceder**: http://localhost:8000
2. **Login**: Usar credenciales de usuario registrado
3. **Seleccionar empresa**: Sistema automáticamente filtra datos por empresa
4. **Gestionar recursos**: Productos, pedidos, inventario, etc.

## Capacidades Avanzadas

✅ Validación de datos en serializers  
✅ Permisos basados en roles y empresa  
✅ Manejo de errores personalizado  
✅ API RESTful completa  
✅ Aislamiento multi-tenant garantizado  
✅ Formularios dinámicos JavaScript  
✅ Interfaz responsive  

## Producción

Para desplegar en producción:

```bash
# Instalar PostgreSQL driver
pip install psycopg2-binary

# Configurar variables de entorno (.env)
# Ejecutar collectstatic
python manage.py collectstatic

# Usar gunicorn o servidor WSGI
```

## Licencia

Proyecto educativo - Evaluación 4 Programación
