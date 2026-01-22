# Guía de Desarrollo - Barber Manager Pro

Guía completa para desarrolladores que desean contribuir, extender o modificar el proyecto.

---

## Tabla de Contenidos

- [Setup del Entorno](#setup-del-entorno)
- [Estructura del Código](#estructura-del-código)
- [Flujo de Desarrollo](#flujo-de-desarrollo)
- [Debugging](#debugging)
- [Mejores Prácticas](#mejores-prácticas)
- [Roadmap y Mejoras Futuras](#roadmap-y-mejoras-futuras)

---

## Setup del Entorno

### Requisitos

- Python 3.10+
- Git
- Editor recomendado: VS Code con extensiones Python

### Instalación para Desarrollo

```bash
# 1. Clonar repositorio
git clone https://github.com/AlexisAcevedo/BarberManager.git
cd BarberManager

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Instalar dependencias de producción
pip install -r requirements.txt

# 4. Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# 5. Configurar .env
cp .env.example .env
# Editar .env y establecer ADMIN_PASSWORD
```

### Dependencias de Desarrollo

El archivo `requirements-dev.txt` incluye:

```txt
# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-asyncio>=0.21.0

# Linting y formateo
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0

# Debugging
ipdb>=0.13.0
```

---

## Estructura del Código

### Convenciones de Naming

| Elemento | Convención | Ejemplo |
|----------|------------|---------|
| **Clases** | PascalCase | `AppointmentService`, `Client` |
| **Funciones/Métodos** | snake_case | `get_all_clients()`, `check_availability()` |
| **Variables** | snake_case | `start_time`, `barber_id` |
| **Constantes** | UPPER_SNAKE_CASE | `MAX_FAILED_ATTEMPTS`, `DEFAULT_START_HOUR` |
| **Archivos** | snake_case | `appointment_service.py`, `auth_service.py` |
| **Carpetas** | lowercase | `services`, `models`, `views` |

### Organización de Imports

Ordenar imports en este orden:

```python
# 1. Librerías estándar de Python
from datetime import datetime, date
from typing import List, Optional

# 2. Librerías de terceros
from sqlalchemy.orm import Session
import flet as ft

# 3. Imports del proyecto
from models.base import Appointment, Client
from services.appointment_service import AppointmentService
from database import get_db
```

### Docstrings

Usar Google Style docstrings:

```python
def create_appointment(
    db: Session,
    client_id: int,
    service_id: int,
    start_time: datetime
) -> Tuple[Optional[Appointment], Optional[str]]:
    """
    Crea un nuevo turno con validación de conflictos.
    
    Args:
        db: Sesión de base de datos
        client_id: ID del cliente
        service_id: ID del servicio
        start_time: Hora de inicio del turno
        
    Returns:
        Tupla de (turno creado, mensaje de error).
        Si éxito: (Appointment, None)
        Si error: (None, "mensaje de error")
        
    Raises:
        ValueError: Si los parámetros son inválidos
    """
    ...
```

---

## Flujo de Desarrollo

### Agregar Nueva Feature

#### 1. Crear Rama

```bash
git checkout -b feature/nombre-de-feature
```

#### 2. Planificar Cambios

Pregúntate:
- ¿Necesito un modelo nuevo? → Modificar `models/base.py`
- ¿Necesito lógica de negocio? → Crear/modificar servicio
- ¿Necesito nueva vista? → Crear en `views/`
- ¿Necesito migración de DB? → Crear con Alembic

---

### Agregar Nuevo Modelo

#### Paso 1: Definir Modelo en `models/base.py`

```python
class Product(Base):
    """Productos de barbería para venta."""
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float, default=0.0)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name='{self.name}')>"
```

#### Paso 2: Crear Migración

```bash
alembic revision --autogenerate -m "add products table"
```

Revisar migración generada en `alembic/versions/`, ajustar si necesario.

#### Paso 3: Aplicar Migración

```bash
alembic upgrade head
```

#### Paso 4: Agregar Tests

Crear `tests/test_product_model.py`:

```python
def test_create_product(db):
    product = Product(name="Gel", price=500.0, stock=10)
    db.add(product)
    db.flush()
    
    assert product.id is not None
    assert product.name == "Gel"
```

---

### Agregar Nuevo Servicio

#### Paso 1: Crear Archivo `services/product_service.py`

```python
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from models.base import Product

class ProductService:
    """Gestión de inventario de productos."""
    
    @classmethod
    def get_all_products(cls, db: Session) -> List[Product]:
        """Obtiene todos los productos."""
        return db.query(Product).filter(
            Product.is_active == True
        ).order_by(Product.name).all()
    
    @classmethod
    def create_product(
        cls, 
        db: Session, 
        name: str, 
        price: float, 
        stock: int = 0
    ) -> Tuple[Optional[Product], Optional[str]]:
        """
        Crea un nuevo producto.
        
        Args:
            db: Sesión de base de datos
            name: Nombre del producto
            price: Precio
            stock: Stock inicial
            
        Returns:
            Tupla (Producto, error)
        """
        # Validaciones
        if not name or len(name.strip()) < 2:
            return None, "Nombre debe tener al menos 2 caracteres"
        
        if price < 0:
            return None, "Precio debe ser mayor o igual a 0"
        
        # Crear producto
        product = Product(
            name=name.strip(),
            price=price,
            stock=stock
        )
        db.add(product)
        db.flush()
        
        return product, None
```

#### Paso 2: Escribir Tests

Crear `tests/test_product_service.py`:

```python
import pytest
from services.product_service import ProductService

def test_create_product_success(db):
    product, error = ProductService.create_product(
        db, name="Gel", price=500.0, stock=10
    )
    
    assert product is not None
    assert error is None
    assert product.name == "Gel"

def test_create_product_invalid_name(db):
    product, error = ProductService.create_product(
        db, name="G", price=500.0
    )
    
    assert product is None
    assert "al menos 2 caracteres" in error
```

---

### Agregar Nueva Vista

#### Paso 1: Crear `views/products_view.py`

```python
import flet as ft
from database import get_db
from services.product_service import ProductService

def create_products_view(page: ft.Page):
    """Vista de productos."""
    
    def load_products():
        """Carga productos desde base de datos."""
        with get_db() as db:
            products = ProductService.get_all_products(db)
            return products
    
    def on_add_product(e):
        """Callback para agregar producto."""
        with get_db() as db:
            product, error = ProductService.create_product(
                db,
                name=name_field.value,
                price=float(price_field.value),
                stock=int(stock_field.value)
            )
            
            if product:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Producto creado"),
                    bgcolor=ft.Colors.GREEN_700
                )
                # Recargar lista
                load_products()
            else:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(error),
                    bgcolor=ft.Colors.RED_700
                )
            
            page.snack_bar.open = True
            page.update()
    
    # UI Components
    name_field = ft.TextField(label="Nombre", width=300)
    price_field = ft.TextField(label="Precio", width=150)
    stock_field = ft.TextField(label="Stock", width=150, value="0")
    
    add_button = ft.ElevatedButton(
        text="Agregar Producto",
        on_click=on_add_product
    )
    
    # Layout
    return ft.Column([
        ft.Text("Gestión de Productos", size=24, weight=ft.FontWeight.BOLD),
        ft.Row([name_field, price_field, stock_field]),
        add_button,
        # Lista de productos...
    ])
```

#### Paso 2: Agregar Ruta en `main.py`

```python
# En función route_change()
elif route == "/products":
    from views.products_view import create_products_view
    content_area.content = create_products_view(page)
```

#### Paso 3: Agregar a Sidebar

```python
# En views/components/sidebar.py
# Agregar item a NavigationRail
ft.NavigationRailDestination(
    icon=ft.Icons.SHOPPING_CART_OUTLINED,
    selected_icon=ft.Icons.SHOPPING_CART,
    label="Productos"
)
```

---

## Debugging

### Logs

El sistema usa logging de Python. Configurar nivel en `.env`:

```env
DEBUG=true
ECHO_SQL=true
```

**Niveles de log**:
- `DEBUG`: Información detallada
- `INFO`: Operaciones normales
- `WARNING`: Situaciones anormales pero manejables
- `ERROR`: Errores

**Usar en código**:

```python
from config import logger

logger.debug("Iniciando proceso de validación")
logger.info(f"Usuario {username} autenticado")
logger.warning(f"Intento de desactivar último barbero activo")
logger.error(f"Error inesperado: {e}")
```

### Debugging en Flet

Flet ejecuta en modo asíncrono, lo que dificulta debugging tradicional.

**Técnicas**:

1. **Print statements** (simple pero efectivo):
```python
print(f"DEBUG: client_id={client_id}, start_time={start_time}")
```

2. **Logs**:
```python
logger.debug(f"Estado del formulario: {form_data}")
```

3. **Breakpoints con ipdb** (instalar `ipdb`):
```python
import ipdb; ipdb.set_trace()
```

### SQL Debugging

Ver queries ejecutadas:

```env
ECHO_SQL=true
```

Esto imprime todas las queries en consola:

```sql
SELECT * FROM appointments WHERE barber_id = ? AND start_time >= ?
```

---

## Mejores Prácticas

### Separación de Responsabilidades

#### ✅ Correcto

```python
# Vista: Solo UI y manejo de eventos
def on_create_client(e):
    with get_db() as db:
        client, error = ClientService.create_client(db, ...)
        # Actualizar UI basado en resultado

# Servicio: Lógica de negocio
class ClientService:
    @classmethod
    def create_client(cls, db, ...):
        # Validaciones
        # Creación
        return client, error
```

#### ❌ Incorrecto

```python
# Vista con lógica de negocio embebida (malo)
def on_create_client(e):
    with get_db() as db:
        # Validar email (esto debería estar en servicio)
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            show_error("Email inválido")
            return
        
        # Crear directamente (bypassing servicio)
        client = Client(name=name, email=email)
        db.add(client)
```

---

### Manejo de Sesiones DB

#### ✅ Correcto: Context Manager

```python
with get_db() as db:
    client = ClientService.create_client(db, ...)
    # Commit automático al salir si no hubo excepción
```

#### ❌ Incorrecto: Sesión manual

```python
db = get_db_session()  # Mal
client = ClientService.create_client(db, ...)
db.commit()  # Fácil olvidar
db.close()   # Fácil olvidar
```

---

### Error Handling

#### ✅ Correcto: Tuplas (result, error)

```python
client, error = ClientService.create_client(db, ...)

if client:
    # Éxito
    update_ui()
else:
    # Error
    show_error(error)
```

#### ❌ Incorrecto: Excepciones para control de flujo

```python
try:
    client = ClientService.create_client(db, ...)
except ClientAlreadyExists:
    show_error("Cliente ya existe")
except InvalidEmail:
    show_error("Email inválido")
# Muchas excepciones = difícil de mantener
```

---

### Validación de Inputs

Siempre validar en el servicio, NO solo en la UI.

#### ✅ Correcto

```python
# UI: Validación básica para UX
if not email_field.value:
    show_error("Email requerido")
    return

# Servicio: Validación real
class ClientService:
    @classmethod
    def create_client(cls, db, email, ...):
        if not email or not validate_email(email):
            return None, "Email inválido"
```

**Razón**: La UI puede ser bypasseada (tests, API futura), pero el servicio siempre se ejecuta.

---

## Roadmap y Mejoras Futuras

### Funcionalidades Planificadas

#### 1. Google Calendar Sync (Implementación Completa)

Actualmente hay un stub en `AppointmentService.sync_to_google()`.

**Tareas**:
- Implementar autenticación OAuth2
- Crear/actualizar eventos en Google Calendar
- Sincronización bidireccional (cambios en Calendar reflejados en app)

**Archivos a modificar**:
- `services/appointment_service.py`
- Nuevo: `services/google_calendar_service.py`
- Agregar credenciales OAuth en `.env`

---

#### 2. API de WhatsApp Business

Actualmente se genera URL manual. Automatizar con API oficial.

**Tareas**:
- Integrar WhatsApp Business API
- Envío automático de recordatorios
- Confirmaciones vía WhatsApp

**Archivos a modificar**:
- `services/notification_service.py`
- Nuevo: `services/whatsapp_service.py`

---

#### 3. Multi-Sede

Soportar múltiples sucursales de barbería.

**Cambios necesarios**:
- Nuevo modelo `Branch` (sucursal)
- Relacionar `Barber` con `Branch`
- Filtrado global por sucursal en UI
- Migración para datos existentes

**Archivos a crear/modificar**:
- `models/base.py`: Add `Branch` model
- `services/branch_service.py`: New
- `views/branches_view.py`: New
- Migración Alembic

---

#### 4. Sistema de Inventario

Gestionar productos vendidos en la barbería.

**Modelos nuevos**:
- `Product`: Productos
- `Sale`: Ventas realizadas

**Vistas nuevas**:
- `products_view.py`: CRUD productos
- `sales_view.py`: Registrar ventas

---

#### 5. Programa de Fidelización

Puntos por visita, descuentos, etc.

**Modelos nuevos**:
- `LoyaltyCard`: Tarjeta de cliente
- `LoyaltyTransaction`: Registro de puntos

---

### Mejoras Técnicas

#### Migración a PostgreSQL

Para producción multi-usuario, cambiar de SQLite a PostgreSQL:

```python
# .env
DATABASE_URL=postgresql://user:pass@localhost:5432/barber_db

# No requiere cambios en código (solo config)
```

**Ventajas**:
- Mejor concurrencia
- Escrituras simultáneas
- Escalabilidad

---

#### Caché de Queries Frecuentes

Implementar caché con Redis para queries de lectura:

```python
# services/appointment_service.py
from functools import lru_cache

@lru_cache(maxsize=128)
def get_business_hours(db):
    # Query cached
```

---

#### CI/CD Pipeline

Configurar GitHub Actions para:

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: pytest
      - name: Check coverage
        run: pytest --cov=. --cov-fail-under=80
```

---

#### Tests de Integración y E2E

Actualmente solo hay tests unitarios. Agregar:

- Tests de integración (múltiples servicios)
- Tests E2E con Selenium/Playwright para UI

---

## Contribuciones

Al contribuir al proyecto:

1. **Fork** el repositorio
2. Crear **rama de feature**
3. **Escribir tests** para nuevos cambios
4. **Documentar** cambios en markdown si corresponde
5. **Seguir convenciones** de código
6. Abrir **Pull Request** con descripción clara

---

## Recursos

- [Flet Documentation](https://flet.dev/docs/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [pytest Documentation](https://docs.pytest.org/)

---

**📚 Documentación Relacionada**:
- [Arquitectura](arquitectura.md) - Arquitectura del sistema
- [API Interna](api_interna.md) - Servicios disponibles
- [Testing](testing.md) - Cómo escribir tests
