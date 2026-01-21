"""
Servicio de configuración para Barber Manager.
Maneja la persistencia de configuración de la aplicación.
"""
from typing import Optional

from sqlalchemy.orm import Session

from models.base import Settings


# Valores de configuración por defecto
DEFAULT_SETTINGS = {
    "business_hours_start": "12",
    "business_hours_end": "20",
    "slot_duration": "15",
}


class SettingsService:
    """
    Capa de servicio para configuración de la aplicación.
    Proporciona operaciones get/set para configuración clave-valor.
    """
    
    @classmethod
    def get_setting(cls, db: Session, key: str) -> Optional[str]:
        """
        Obtiene el valor de una configuración por clave.
        
        Args:
            db: Sesión de base de datos
            key: Clave de la configuración
            
        Retorna:
            Valor de la configuración o None si no se encuentra
        """
        setting = db.query(Settings).filter(Settings.key == key).first()
        if setting:
            return setting.value
        return DEFAULT_SETTINGS.get(key)
    
    @classmethod
    def set_setting(cls, db: Session, key: str, value: str) -> None:
        """
        Establece el valor de una configuración.
        Crea la configuración si no existe.
        
        Args:
            db: Sesión de base de datos
            key: Clave de la configuración
            value: Valor de la configuración
        """
        setting = db.query(Settings).filter(Settings.key == key).first()
        if setting:
            setting.value = value
        else:
            setting = Settings(key=key, value=value)
            db.add(setting)
    
    @classmethod
    def get_business_hours(cls, db: Session) -> tuple:
        """
        Obtiene la configuración de horario de atención.
        
        Args:
            db: Sesión de base de datos
            
        Retorna:
            Tupla de (hora_inicio, hora_fin) como enteros
        """
        start = cls.get_setting(db, "business_hours_start")
        end = cls.get_setting(db, "business_hours_end")
        return int(start), int(end)
    
    @classmethod
    def set_business_hours(cls, db: Session, start_hour: int, end_hour: int) -> None:
        """
        Establece la configuración de horario de atención.
        
        Args:
            db: Sesión de base de datos
            start_hour: Hora de apertura (0-23)
            end_hour: Hora de cierre (0-23)
        """
        cls.set_setting(db, "business_hours_start", str(start_hour))
        cls.set_setting(db, "business_hours_end", str(end_hour))
