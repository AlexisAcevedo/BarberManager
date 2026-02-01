# Guía de Despliegue en Producción

Esta guía detalla los pasos para desplegar **Barber Manager** en un entorno de producción seguro y estable.

## 📋 Requisitos Previos

- Python 3.10 o superior
- pip (gestor de paquetes)
- Git

## 🚀 Pasos de Instalación

1.  **Clonar el Repositorio**
    ```bash
    git clone <url-del-repo>
    cd Barberia
    ```

2.  **Crear Entorno Virtual**
    Se recomienda aislar las dependencias:
    ```bash
    python -m venv venv
    
    # Windows
    venv\Scripts\activate
    
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Instalar Dependencias**
    ```bash
    pip install -r requirements.txt
    ```
    *Nota: Si usas una versión específica de Flet, asegura que coincida en requirements.txt.*

4.  **Configuración de Entorno (.env)**
    Crea un archivo `.env` en la raíz (usa `.env.example` como base).
    **Variables CRÍTICAS**:
    
    ```ini
    # Seguridad
    ADMIN_PASSWORD=TuPasswordSuperSegura123!
    
    # Base de Datos
    DATABASE_URL=sqlite:///barber_manager.db
    
    # Logging
    LOG_FILE=logs/production.log
    DEBUG=False  # IMPORTANTE: False para producción
    ```

5.  **Inicialización de Base de Datos**
    Al ejecutar la aplicación por primera vez, se crearán las tablas y usuarios semilla automáticamente.
    ```bash
    python main.py
    ```

## 🛡️ Mantenimiento

### Copias de Seguridad (Backups)
Se incluye un script automatizado en `scripts/backup_db.py`.
Ejecútalo periódicamente (ej. vía Tarea Programada de Windows o Cron):

```bash
python scripts/backup_db.py
```
Los backups se guardarán en la carpeta `backups/` y se rotarán automáticamente manteniendo los últimos 10.

### Logs
Revisa `logs/production.log` para monitorear errores o actividad sospechosa (ej. múltiples intentos fallidos de login).

## ⚠️ Solución de Problemas

- **Login Fallido**: Si olvidas la contraseña de admin, deberás acceder a la base de datos manualmente o resetearla (¡Cuidado con perder datos!).
- **Puerto Ocupado**: Flet busca puertos libres automáticamente. Si falla, verifica que no haya otro proceso de Barber Manager corriendo.

---
**Soporte Técnico**: Contactar al equipo de desarrollo ante incidencias críticas.
