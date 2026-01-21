# 🪒 Barber Manager Pro

Sistema de gestión de turnos para barberías. Aplicación de escritorio construida con **Flet** (UI) y **SQLAlchemy** (ORM).

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flet](https://img.shields.io/badge/Flet-0.80+-green)
![SQLite](https://img.shields.io/badge/SQLite-3-orange)

## ✨ Características

- 📅 **Agenda semanal** con vista de calendario interactiva
- 👥 **Gestión de clientes** con búsqueda y CRUD completo
- 💈 **Catálogo de servicios** con precios y duraciones
- 📊 **Reportes y arqueo de caja** diario y por período
- 👨‍💼 **Multi-barbero** con asignación de turnos
- 🔔 **Notificaciones WhatsApp** para recordatorios
- 🔐 **Autenticación** con hash bcrypt

## 🚀 Instalación

### Requisitos previos
- Python 3.10 o superior
- pip (gestor de paquetes)

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/AlexisAcevedo/barberia.git
cd barberia

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la aplicación
python main.py
```

## 📖 Uso

### Credenciales por defecto
- **Usuario:** `admin`
- **Contraseña:** `admin`

### Navegación
- **Agenda:** Vista principal con calendario semanal
- **Clientes:** Gestión de base de clientes
- **Reportes:** Estadísticas y arqueo de caja
- **Servicios:** Catálogo de servicios ofrecidos
- **Configuración:** Horarios de atención

## 📁 Estructura del Proyecto

```
barberia/
├── main.py                  # Punto de entrada
├── database.py              # Conexión y sesiones de BD
├── config.py                # Configuración centralizada
├── models/
│   └── base.py              # Modelos ORM (Barber, Client, etc.)
├── services/
│   ├── appointment_service.py
│   ├── auth_service.py
│   ├── client_service.py
│   └── ...                  # Lógica de negocio
├── repositories/
│   ├── base_repository.py   # Repositorio genérico
│   └── appointment_repository.py
├── views/
│   ├── agenda_view.py       # Vista principal
│   ├── login_view.py
│   ├── clients_view.py
│   └── ...                  # Vistas de UI
├── utils/
│   └── validators.py        # Validadores de entrada
└── tests/                   # Tests unitarios
```

## 🏗️ Arquitectura

El proyecto sigue el patrón **MVC** (Modelo-Vista-Controlador) adaptado:

- **Modelos:** SQLAlchemy ORM en `models/base.py`
- **Servicios:** Lógica de negocio en `services/`
- **Repositorios:** Acceso a datos en `repositories/`
- **Vistas:** UI con Flet en `views/`

Ver [docs/arquitectura.md](docs/arquitectura.md) para más detalles.

## 🧪 Tests

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=. --cov-report=html
```

## 📋 Dependencias principales

| Paquete | Versión | Descripción |
|---------|---------|-------------|
| flet | 0.80+ | Framework UI |
| sqlalchemy | 2.0+ | ORM |
| bcrypt | 4.0+ | Hash de contraseñas |
| alembic | 1.12+ | Migraciones |

## 🔧 Configuración

Variables de entorno opcionales (crear archivo `.env`):

```env
DATABASE_URL=sqlite:///barber_manager.db
ECHO_SQL=false
DEBUG=false
```

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE) para más detalles.

## 👥 Contribuir

1. Fork el proyecto
2. Crea tu rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'feat: agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request
