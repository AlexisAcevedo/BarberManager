"""
Configuración centralizada para la aplicación Barber Manager.
Usa variables de entorno con valores por defecto sensibles.
"""
import os
import logging
from typing import Optional


class BusinessConfig:
    """Configuración de lógica de negocio."""
    
    # Horario de trabajo (formato 24h)
    HOURS_START: int = 12  # 12:00 PM
    HOURS_END: int = 20    # 8:00 PM
    
    # Intervalos de turnos
    SLOT_DURATION_MINUTES: int = 15
    
    # Duraciones de servicios por defecto
    DEFAULT_CORTE_DURATION: int = 30
    DEFAULT_BARBA_DURATION: int = 15
    DEFAULT_COMBO_DURATION: int = 40


class DatabaseConfig:
    """Configuración de base de datos."""
    
    # URL de base de datos - puede ser sobrescrita con variable de entorno
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///barber_manager.db")
    
    # Configuración de SQLAlchemy
    ECHO_SQL: bool = os.getenv("ECHO_SQL", "false").lower() == "true"
    

class AppConfig:
    """Configuración general de la aplicación."""
    
    # Información de la aplicación
    APP_NAME: str = "Barber Manager"
    APP_VERSION: str = "1.0.0"
    
    # Configuración de ventana
    WINDOW_WIDTH: int = int(os.getenv("WINDOW_WIDTH", "1280"))
    WINDOW_HEIGHT: int = int(os.getenv("WINDOW_HEIGHT", "780"))
    WINDOW_MIN_WIDTH: int = 900
    WINDOW_MIN_HEIGHT: int = 600
    
    # Tema
    DARK_MODE: bool = True
    
    # Modo debug
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"


class LoggingConfig:
    """Configuración de logging."""
    
    # Nivel de log
    LEVEL: int = logging.DEBUG if AppConfig.DEBUG else logging.INFO
    
    # Formato de log
    FORMAT: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
    
    # Archivo de log (opcional)
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE", None)


def setup_logging() -> logging.Logger:
    """
    Configura el logging de la aplicación.
    
    Retorna:
        Logger: Logger raíz configurado
    """
    # Crear formateador
    formatter = logging.Formatter(
        LoggingConfig.FORMAT,
        datefmt=LoggingConfig.DATE_FORMAT
    )
    
    # Configurar logger raíz
    root_logger = logging.getLogger("barber_manager")
    root_logger.setLevel(LoggingConfig.LEVEL)
    
    # Handler de consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Handler de archivo (si está configurado)
    if LoggingConfig.LOG_FILE:
        file_handler = logging.FileHandler(LoggingConfig.LOG_FILE)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    return root_logger


# Inicializar logger
logger = setup_logging()
