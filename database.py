"""
Configuración y gestión de sesiones de base de datos para Barber Manager.
Maneja la conexión SQLite, fábrica de sesiones e inicialización de datos semilla.
"""
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from models.base import Base, Service, Settings, Barber, User
from config import DatabaseConfig, logger

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
    """
    from services.auth_service import AuthService
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
                password="admin", 
                role="admin",
                barber_id=default_barber.id
            )
            logger.info("Datos semilla: Usuario admin creado (admin/admin)")


def reset_db() -> None:
    """
    Reinicia la base de datos eliminando todas las tablas y recreándolas.
    ¡ADVERTENCIA: Esto eliminará todos los datos!
    """
    Base.metadata.drop_all(bind=engine)
    init_db()
