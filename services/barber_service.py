"""
Servicio de barberos para Barber Manager.
Maneja operaciones CRUD de barberos.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from models.base import Barber


class BarberService:
    """Capa de servicio para gestión de barberos."""
    
    @staticmethod
    def get_all_barbers(db: Session) -> List[Barber]:
        """
        Obtiene todos los barberos activos.
        
        Args:
            db: Sesión de base de datos
            
        Retorna:
            Lista de barberos activos
        """
        return db.query(Barber).filter(Barber.is_active == True).all()

    @staticmethod
    def get_barber_by_id(db: Session, barber_id: int) -> Optional[Barber]:
        """
        Obtiene un barbero por su ID.
        
        Args:
            db: Sesión de base de datos
            barber_id: ID del barbero
            
        Retorna:
            Barbero si se encuentra, None en caso contrario
        """
        return db.query(Barber).filter(Barber.id == barber_id).first()

    @staticmethod
    def create_barber(db: Session, name: str, color: str = "#2196F3") -> Barber:
        """
        Crea un nuevo barbero.
        
        Args:
            db: Sesión de base de datos
            name: Nombre del barbero
            color: Color de identificación en UI
            
        Retorna:
            Barbero creado
        """
        barber = Barber(name=name, color=color)
        db.add(barber)
        db.flush()
        return barber
