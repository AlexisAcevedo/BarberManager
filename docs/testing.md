# Documentación de Testing - Barber Manager Pro

Guía completa de la estrategia de testing, ejecución de tests y escritura de nuevos tests para el proyecto.

---

## Tabla de Contenidos

- [Filosofía de Testing](#filosofía-de-testing)
- [Setup de Testing](#setup-de-testing)
- [Estructura de Tests](#estructura-de-tests)
- [Ejecutar Tests](#ejecutar-tests)
- [Escribir Nuevos Tests](#escribir-nuevos-tests)
- [Tests Existentes](#tests-existentes)
- [Coverage](#coverage)

---

## Filosofía de Testing

### Principios

1. **Test de lógica de negocio, no de bibliotecas de terceros**
   - ✅ Testear servicios y validaciones
   - ❌ No testear SQLAlchemy o Flet directamente

2. **Tests independientes**
   - Cada test debe ejecutarse independientemente
   - No compartir estado entre tests
   - Usar fixtures para setup/teardown

3. **Tests significativos**
   - Testear comportamiento, no implementación
   - Tests deben documentar cómo usar el código

4. **Pirámide de testing**
   ```
          / E2E \
         /       \
        / Integration \
       /_______________\
      /   Unit Tests    \
     /___________________\
   ```
   - Mayoría: Tests unitarios (rápidos, aislados)
   - Algunos: Tests de integración (múltiples componentes)
   - Pocos: Tests E2E (lentos, frágiles)

---

## Setup de Testing

### Instalar Dependencias

```bash
pip install -r requirements-dev.txt
```

Incluye:
- `pytest`: Framework de testing
- `pytest-cov`: Cobertura de código
- `pytest-asyncio`: Testing de código asíncrono

### Configuración de pytest

Archivo `pytest.ini` (crear en raíz si no existe):

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --strict-markers
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
```

---

## Estructura de Tests

### Directorio `tests/`

```
tests/
├── __init__.py
├── conftest.py                      # Fixtures compartidos
├── test_appointment_service.py      # Tests de servicio de turnos
├── test_appointment_repository.py   # Tests de repositorio
├── test_auth_service.py             # Tests de autenticación
├── test_client_service.py           # Tests de servicio de clientes
├── test_service_service.py          # Tests de servicio de servicios
├── test_base_repository.py          # Tests de repositorio base
├── test_barber_service.py           # (por crear)
├── test_notification_service.py     # Tests de notificaciones
├── test_settings_service.py         # Tests de configuración
└── test_validators.py               # Tests de validadores
```

### Archivo `conftest.py`

Contiene fixtures compartidos por todos los tests:

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base

@pytest.fixture(scope="function")
def db():
    """
    Crea una base de datos en memoria para cada test.
    Se destruye automáticamente al finalizar el test.
    """
    # Crear engine en memoria
    engine = create_engine("sqlite:///:memory:")
    
    # Crear todas las tablas
    Base.metadata.create_all(engine)
    
    # Crear sesión
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    # Cleanup
    session.close()
    engine.dispose()

@pytest.fixture
def sample_barber(db):
    """Fixture: Barbero de ejemplo."""
    from models.base import Barber
    barber = Barber(name="Test Barber", color="#FF0000")
    db.add(barber)
    db.flush()
    return barber

@pytest.fixture
def sample_client(db):
    """Fixture: Cliente de ejemplo."""
    from models.base import Client
    client = Client(
        name="John Doe",
        email="john@example.com",
        phone="+1234567890"
    )
    db.add(client)
    db.flush()
    return client
```

**Ventajas de fixtures**:
- Reutilización de código
- Setup/teardown automático
- Datos de prueba consistentes

---

## Ejecutar Tests

### Todos los Tests

```bash
pytest
```

### Tests Específicos

```bash
# Un archivo
pytest tests/test_auth_service.py

# Una clase
pytest tests/test_auth_service.py::TestAuthService

# Una función
pytest tests/test_auth_service.py::test_authenticate_success
```

### Con Cobertura

```bash
# Cobertura en consola
pytest --cov=. --cov-report=term

# Cobertura HTML (más detallada)
pytest --cov=. --cov-report=html

# Abrir reporte
# Windows: start htmlcov/index.html
# Linux: xdg-open htmlcov/index.html
```

### Modo Verbose

```bash
pytest -v
```

Output:
```
tests/test_auth_service.py::test_hash_password PASSED          [ 10%]
tests/test_auth_service.py::test_verify_password_correct PASSED[ 20%]
tests/test_auth_service.py::test_authenticate_success PASSED   [ 30%]
...
```

### Ejecutar Solo Marcados

```bash
# Solo tests unitarios
pytest -m unit

# Solo tests lentos
pytest -m slow
```

---

## Escribir Nuevos Tests

### Estructura de un Test

```python
def test_nombre_descriptivo(db, fixture1, fixture2):
    """
    Descripción de lo que testea.
    
    Given: Estado inicial
    When: Acción realizada
    Then: Resultado esperado
    """
    # Arrange (preparar)
    # Setup de datos necesarios
    
    # Act (actuar)
    # Ejecutar función a testear
    
    # Assert (verificar)
    # Verificar resultado esperado
```

### Ejemplo: Test de Servicio

```python
# tests/test_client_service.py
from services.client_service import ClientService

def test_create_client_success(db):
    """
    Test: Crear cliente exitosamente.
    
    Given: Base de datos vacía
    When: Crear cliente con datos válidos
    Then: Cliente se crea correctamente
    """
    # Arrange
    name = "Juan Pérez"
    email = "juan@example.com"
    phone = "+549111234567"
    
    # Act
    client, error = ClientService.create_client(
        db, name, email, phone
    )
    
    # Assert
    assert client is not None, "Cliente no debería ser None"
    assert error is None, "No debería haber error"
    assert client.name == name
    assert client.email == email
    assert client.id is not None, "Cliente should have ID"

def test_create_client_duplicate_email(db):
    """
    Test: No permitir email duplicado.
    
    Given: Cliente existente con email
    When: Intentar crear otro con mismo email
    Then: Retorna error
    """
    # Arrange
    email = "test@example.com"
    # Crear primer cliente
    ClientService.create_client(db, "Primero", email)
    
    # Act
    client, error = ClientService.create_client(
        db, "Segundo", email
    )
    
    # Assert
    assert client is None, "No debería crear cliente"
    assert error is not None, "Debería retornar error"
    assert "email" in error.lower()

def test_create_client_invalid_email(db):
    """
    Test: Validar formato de email.
    
    Given: Base de datos
    When: Crear cliente con email inválido
    Then: Retorna error de validación
    """
    # Act
    client, error = ClientService.create_client(
        db, "Test", "email-invalido"
    )
    
    # Assert
    assert client is None
    assert "inválido" in error.lower() or "invalid" in error.lower()
```

### Usar Fixtures

```python
def test_update_client(db, sample_client):
    """Test usando fixture de cliente."""
    # sample_client ya existe en DB
    client_id = sample_client.id
    
    # Act
    updated, error = ClientService.update_client(
        db, client_id, name="Nuevo Nombre"
    )
    
    # Assert
    assert updated is not None
    assert updated.name == "Nuevo Nombre"
```

### Testear Excepciones

```python
import pytest

def test_function_raises_error():
    """Test que verifica que se lanza excepción."""
    with pytest.raises(ValueError, match="mensaje esperado"):
        # Code que debería lanzar ValueError
        raise ValueError("mensaje esperado")
```

### Parametrizar Tests

Ejecutar el mismo test con múltiples sets de datos:

```python
import pytest

@pytest.mark.parametrize("password,expected_valid", [
    ("short", False),          # Muy corto
    ("MediumPass123", True),   # Válido
    ("VeryLongPasswordThatIsValid123", True),  # Largo válido
])
def test_password_validation(password, expected_valid):
    """Test de validación de password con múltiples casos."""
    from utils.validators import validate_password
    
    is_valid, _ = validate_password(password)
    assert is_valid == expected_valid
```

---

## Tests Existentes

### test_appointment_service.py

**Cobertura**: Servicio de turnos

**Tests implementados**:
- `test_get_available_slots()`: Cálculo de disponibilidad
- `test_create_appointment_success()`: Creación exitosa
- `test_create_appointment_conflict()`: Detección de conflictos
- `test_update_appointment_status()`: Cambio de estado

**Ejemplo**:
```python
def test_create_appointment_conflict(db, sample_client, sample_service, sample_barber):
    """
    Test: Detectar conflicto de horario.
    
    Given: Turno existente de 14:00 a 14:30
    When: Intentar crear turno de 14:15 a 14:45
    Then: Retorna error de conflicto
    """
    from datetime import datetime
    from services.appointment_service import AppointmentService
    
    # Crear primer turno
    start1 = datetime(2026, 1, 25, 14, 0)
    AppointmentService.create_appointment(
        db, sample_client.id, sample_service.id,
        sample_barber.id, start1
    )
    
    # Intentar crear turno conflictivo
    start2 = datetime(2026, 1, 25, 14, 15)
    appointment, error = AppointmentService.create_appointment(
        db, sample_client.id, sample_service.id,
        sample_barber.id, start2
    )
    
    assert appointment is None
    assert "disponible" in error.lower()
```

---

### test_auth_service.py

**Cobertura**: Autenticación y rate limiting

**Tests implementados**:
- `test_hash_password()`: Hashing de contraseñas
- `test_verify_password()`: Verificación de hash
- `test_authenticate_success()`: Login exitoso
- `test_authenticate_rate_limiting()`: Bloqueo tras 5 intentos

**Ejemplo**:
```python
def test_authenticate_rate_limiting(db, sample_user):
    """
    Test: Rate limiting tras 5 intentos fallidos.
    
    Given: Usuario existente
    When: 5 intentos fallidos consecutivos
    Then: Usuario se bloquea
    """
    from services.auth_service import AuthService
    
    # 5 intentos fallidos
    for i in range(5):
        user, error = AuthService.authenticate(
            db, "testuser", "wrong_password"
        )
        assert user is None
    
    # Sexto intento: debería estar bloqueado
    user, error = AuthService.authenticate(
        db, "testuser", "wrong_password"
    )
    
    assert "bloqueado" in error.lower() or "locked" in error.lower()
```

---

### test_validators.py

**Cobertura**: Validadores de entrada

**Tests implementados**:
- `test_validate_email_valid()`: Emails válidos
- `test_validate_email_invalid()`: Emails inválidos
- `test_validate_phone()`: Formatos de teléfono
- `test_validate_name()`: Validación de nombres

**Ejemplo**:
```python
@pytest.mark.parametrize("email,expected", [
    ("test@example.com", True),
    ("user.name@domain.co.uk", True),
    ("invalid-email", False),
    ("@example.com", False),
    ("test@", False),
])
def test_validate_email(email, expected):
    """Test de validación de email con casos."""
    from utils.validators import validate_email
    
    is_valid, _ = validate_email(email)
    assert is_valid == expected
```

---

### test_base_repository.py

**Cobertura**: Repositorio genérico

**Tests implementados**:
- `test_create()`: Crear entidad
- `test_get_by_id()`: Obtener por ID
- `test_get_all()`: Listar todas
- `test_update()`: Actualizar
- `test_delete()`: Eliminar

---

## Coverage

### Coverage Actual

| Módulo | Cobertura |
|--------|-----------|
| `services/` | ~85% |
| `repositories/` | ~90% |
| `utils/validators.py` | ~95% |
| `models/` | ~75% |
| **Total** | **~87%** |

### Ver Cobertura Detallada

```bash
pytest --cov=. --cov-report=html
```

Abrir `htmlcov/index.html` para ver:
- Qué líneas están cubiertas (verde)
- Qué líneas NO están cubiertas (rojo)
- Porcentaje por archivo

### Objetivo de Cobertura

- **Mínimo aceptable**: 80%
- **Objetivo**: 90%
- **Crítico cubrir**:
  - Servicios (lógica de negocio)
  - Validadores (seguridad)
  - Repositorios (acceso a datos)

---

## UI Testing (Consideraciones para Flet)

### Desafío

Flet ejecuta código asíncrono y renderiza en Flutter. Testing de UI es complejo.

### Estrategias

#### 1. Separar Lógica de UI

```python
# ❌ Malo: Lógica mezclada con UI
def on_button_click(e):
    # Validación inline
    if not email_field.value:
        show_error()
        return
    # Crear cliente inline
    client = Client(...)
    db.add(client)
    db.commit()

# ✅ Bueno: UI llama a servicio
def on_button_click(e):
    with get_db() as db:
        client, error = ClientService.create_client(
            db, email_field.value
        )
        if client:
            show_success()
        else:
            show_error(error)
```

Ahora puedes testear `ClientService` sin tocar UI.

#### 2. Tests de Integración Manuales

Para verificar UI manualmente, crear checklist:

```markdown
## Checklist de UI Testing

### Vista de Clientes
- [ ] Cargar lista de clientes
- [ ] Crear nuevo cliente con datos válidos
- [ ] Intentar crear cliente con email duplicado (debe mostrar error)
- [ ] Buscar cliente por nombre
- [ ] Editar cliente existente
- [ ] Eliminar cliente sin turnos
- [ ] Intentar eliminar cliente con turnos (debe prevenir)
```

#### 3. Tests E2E (Futuro)

Usar Selenium o Playwright para tests automatizados de UI.

---

## Best Practices

### 1. Nombres Descriptivos

```python
# ❌ Malo
def test_1():
    ...

# ✅ Bueno
def test_create_client_with_duplicate_email_returns_error():
    ...
```

### 2. Un Assert por Concepto

```python
# ✅ Aceptable: Múltiples asserts del mismo concepto
def test_create_client():
    client, error = ClientService.create_client(...)
    assert client is not None
    assert client.name == "Expected"
    assert client.email == "expected@example.com"

# ❌ Malo: Testear múltiples conceptos
def test_everything():
    # Test creación
    client, _ = ClientService.create_client(...)
    assert client is not None
    
    # Test actualización (debería ser test separado)
    updated, _ = ClientService.update_client(...)
    assert updated is not None
```

### 3. Evitar Dependencias entre Tests

```python
# ❌ Malo: Test depende de otro
def test_create_client(db):
    global created_client
    created_client, _ = ClientService.create_client(...)

def test_update_client(db):
    # Asume que test_create_client ya corrió
    ClientService.update_client(db, created_client.id, ...)

# ✅ Bueno: Cada test es independiente
def test_update_client(db, sample_client):
    # sample_client es fixture, garantizada
    ClientService.update_client(db, sample_client.id, ...)
```

### 4. Test de Edge Cases

No solo testear el "happy path":

```python
def test_create_client_success(db):
    """Happy path."""
    ...

def test_create_client_empty_name(db):
    """Edge case: nombre vacío."""
    ...

def test_create_client_very_long_name(db):
    """Edge case: nombre de 500 caracteres."""
    ...

def test_create_client_special_characters_in_name(db):
    """Edge case: caracteres especiales."""
    ...
```

---

## Debugging Tests Fallidos

### Ver Detalles de Error

```bash
pytest -v
```

### Ver Output de Print

```bash
pytest -s
```

### Ejecutar en Modo Debug

```bash
pytest --pdb
```

Si un test falla, pytest abre debugger en el punto de falla.

### Ver Logs en Tests

```python
import logging

def test_something(caplog):
    """caplog es fixture de pytest."""
    with caplog.at_level(logging.INFO):
        # Código que genera logs
        ...
    
    # Verificar que se generó log esperado
    assert "mensaje esperado" in caplog.text
```

---

## Conclusión

Una suite de tests robusta es esencial para:

- ✅ **Confianza**: Cambios sin romper funcionalidad existente
- ✅ **Documentación**: Tests muestran cómo usar el código
- ✅ **Refactoring seguro**: Detectar regresiones inmediatamente
- ✅ **Calidad**: Forzar diseño testeable (mejor arquitectura)

**Regla de oro**: Si creas nueva funcionalidad, escribe tests. Si encuentras un bug, escribe test que lo reproduzca, luego arréglalo.

---

**📚 Documentación Relacionada**:
- [Guía de Desarrollo](guia_desarrollo.md) - Setup y mejores prácticas
- [API Interna](api_interna.md) - Servicios a testear
- [Arquitectura](arquitectura.md) - Estructura del código
