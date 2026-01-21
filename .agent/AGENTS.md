# Barber Manager Pro - Contexto para Asistentes IA

## Descripción del Proyecto
Sistema de gestión de turnos para barberías. Aplicación de escritorio construida con Flet (UI) y SQLAlchemy (ORM) siguiendo arquitectura MVC.

## Stack Tecnológico
- **Lenguaje:** Python 3.10+
- **UI Framework:** Flet 0.80+
- **ORM:** SQLAlchemy 2.0+
- **Base de datos:** SQLite
- **Autenticación:** bcrypt
- **Migraciones:** Alembic

## Estructura del Proyecto
```
barberia/
├── main.py              # Punto de entrada, enrutamiento
├── database.py          # Conexión BD, sesiones
├── config.py            # Configuración centralizada
├── models/base.py       # Modelos ORM
├── services/            # Lógica de negocio
├── repositories/        # Acceso a datos
├── views/               # UI con Flet
├── utils/               # Validadores
├── tests/               # Tests unitarios
└── docs/                # Documentación
```

## Patrones de Código

### Servicios
Los servicios retornan tuplas `(resultado, error)`:
```python
client, error = ClientService.create_client(db, name, email)
if error:
    # Manejar error
```

### Sesiones de BD
Siempre usar context manager:
```python
with get_db() as db:
    # operaciones
```

### Vistas Flet
Las vistas son funciones que retornan `ft.Control`:
```python
def create_example_view(page: ft.Page) -> ft.Control:
    return ft.Column(controls=[...])
```

## Convenciones

### Idioma
- **Código:** Variables y funciones en inglés
- **Comentarios/Docstrings:** Español
- **UI/Mensajes de usuario:** Español

### Validaciones
Usar validadores de `utils/validators.py` que retornan `Tuple[bool, Optional[str]]`.

### Estados de Turnos
- `pending`: Agendado, pendiente
- `confirmed`: Completado/atendido
- `cancelled`: Cancelado

## Comandos Frecuentes
```bash
# Ejecutar aplicación
python main.py

# Ejecutar tests
pytest

# Crear migración
alembic revision --autogenerate -m "descripcion"

# Aplicar migraciones
alembic upgrade head
```

## Credenciales por Defecto
- Usuario: `admin`
- Contraseña: `admin`

## Archivos Clave

| Archivo | Propósito |
|---------|-----------|
| `main.py` | Enrutamiento y layout principal |
| `services/appointment_service.py` | Lógica de turnos y disponibilidad |
| `views/agenda_view.py` | Vista principal de calendario |
| `models/base.py` | Definición de entidades |

## Notas para IA
- La versión de Flet es 0.80.x - NO usar APIs deprecadas
- Los botones deben usar `content=ft.Text("...")` en lugar de `text="..."`
- Usar `page.data` para estado de sesión, no `page.session`
- Los mensajes de error ya están en español en los servicios
