"""
Configuración y gestión de sesiones de base de datos para Barber Manager.
Maneja la conexión SQLite, fábrica de sesiones e inicialización de datos semilla.
"""
import os
import logging
from contextlib import contextmanager
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from models.base import Base, Service, Settings, Barber, User
from config import DatabaseConfig

# Cargar variables de entorno desde .env
load_dotenv()

logger = logging.getLogger("barber_manager.database")

# Crear engine con optimizaciones para SQLite
engine = create_engine(
    DatabaseConfig.DATABASE_URL,
    echo=DatabaseConfig.ECHO_SQL,
    connect_args={"check_same_thread": False}  # Requerido para SQLite con hilos
)

# Fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Context manager para sesiones de base de datos.
    Asegura la limpieza apropiada de la sesión después de su uso.
    
    Uso:
        with get_db() as db:
            db.query(Client).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_session() -> Session:
    """
    Obtiene una nueva sesión de base de datos.
    El llamador es responsable de cerrar la sesión.
    
    Retorna:
        Session: Una nueva sesión de SQLAlchemy
    """
    return SessionLocal()


def init_db() -> None:
    """
    Inicializa la base de datos.
    Crea todas las tablas y puebla datos semilla si está vacía.
    """
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    # Poblar datos semilla
    _seed_services()
    _seed_auth()


def _seed_services() -> None:
    """
    Puebla servicios por defecto si la tabla Service está vacía.
    
    Servicios por defecto:
    - Corte (30 min)
    - Barba (15 min)  
    - Combo Corte+Barba (40 min)
    """
    with get_db() as db:
        # Verificar si ya existen servicios
        existing_count = db.query(Service).count()
        if existing_count > 0:
            return
        
        # Definir servicios por defecto
        default_services = [
            Service(name="Corte", duration=30, price=0.0, is_active=True),
            Service(name="Barba", duration=15, price=0.0, is_active=True),
            Service(name="Combo Corte+Barba", duration=40, price=0.0, is_active=True),
        ]
        
        # Agregar todos los servicios
        for service in default_services:
            db.add(service)
        
        logger.info("Datos semilla: Servicios por defecto creados exitosamente")


def _seed_auth() -> None:
    """
    Puebla Barbero y usuario Admin por defecto si están vacíos.
    REQUIERE: Variable de entorno ADMIN_PASSWORD configurada.
    """
    import os
    from services.auth_service import AuthService
    
    # Obtener contraseña admin de variable de entorno
    admin_password = os.getenv("ADMIN_PASSWORD")
    if not admin_password:
        raise ValueError(
            "ADMIN_PASSWORD no está configurada en el archivo .env\n"
            "Por seguridad, debes establecer una contraseña segura para el usuario admin.\n"
            "Copia .env.example a .env y configura ADMIN_PASSWORD."
        )
    
    with get_db() as db:
        # 1. Crear Barbero por defecto si no existe ninguno
        if db.query(Barber).count() == 0:
            default_barber = Barber(id=1, name="Barbero Principal", color="#7E57C2")
            db.add(default_barber)
            db.flush()
            logger.info("Datos semilla: Barbero por defecto creado")
        else:
            default_barber = db.query(Barber).first()

        # 2. Crear usuario admin si no existe ninguno
        if db.query(User).count() == 0:
            AuthService.create_user(
                db, 
                username="admin", 
                password=admin_password, 
                role="admin",
                barber_id=default_barber.id
            )
            logger.info("Datos semilla: Usuario admin creado con contraseña desde .env")


def reset_db() -> None:
    """
    Reinicia la base de datos eliminando todas las tablas y recreándolas.
    ¡ADVERTENCIA: Esto eliminará todos los datos!
    
    SOLO PARA DESARROLLO: Esta función está deshabilitada en producción.
    Requiere confirmación interactiva para prevenir pérdida accidental de datos.
    """
    import os
    
    # Verificar que no estamos en producción
    environment = os.getenv("ENVIRONMENT", "development")
    if environment == "production":
        raise RuntimeError(
            "reset_db() está deshabilitado en producción por seguridad.\n"
            "Si realmente necesitas resetear la base de datos en producción,\n"
            "hazlo manualmente eliminando el archivo .db"
        )
    
    # Requiere confirmación explícita
    print("\n" + "="*60)
    print("⚠️  ADVERTENCIA: OPERACIÓN DESTRUCTIVA")
    print("="*60)
    print("Estás a punto de ELIMINAR TODOS LOS DATOS de la base de datos.")
    print("Esto incluye: clientes, turnos, servicios, usuarios, etc.")
    print("Esta acción NO SE PUEDE DESHACER.")
    print("="*60)
    
    confirmation = input("\nEscribe 'CONFIRMAR' para continuar: ")
    
    if confirmation != "CONFIRMAR":
        print("❌ Operación cancelada. No se eliminaron datos.")
        return
    
    # Confirmación adicional
    final_check = input("¿Estás ABSOLUTAMENTE seguro? (sí/no): ")
    if final_check.lower() != "sí":
        print("❌ Operación cancelada. No se eliminaron datos.")
        return
    
    logger.warning("Usuario confirmó reset de base de datos")
    Base.metadata.drop_all(bind=engine)
    init_db()
    print("✅ Base de datos reseteada exitosamente.")
