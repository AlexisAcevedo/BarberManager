"""
Servicio de barberos para Barber Manager.
Maneja operaciones CRUD de barberos.
"""
from typing import List, Optional, Tuple
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.base import Barber, Appointment


class BarberService:
    """Capa de servicio para gestión de barberos."""
    
    @staticmethod
    def get_all_barbers(db: Session, include_inactive: bool = False) -> List[Barber]:
        """
        Obtiene todos los barberos.
        
        Args:
            db: Sesión de base de datos
            include_inactive: Si True, incluye barberos inactivos
            
        Retorna:
            Lista de barberos
        """
        query = db.query(Barber)
        if not include_inactive:
            query = query.filter(Barber.is_active == True)
        return query.order_by(Barber.name).all()

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
    def create_barber(db: Session, name: str, color: str = "#2196F3") -> Tuple[Optional[Barber], Optional[str]]:
        """
        Crea un nuevo barbero.
        
        Args:
            db: Sesión de base de datos
            name: Nombre del barbero
            color: Color de identificación en UI (formato #RRGGBB)
            
        Retorna:
            Tupla (Barbero creado, mensaje de error)
        """
        # Validar nombre
        if not name or len(name.strip()) < 2:
            return None, "El nombre debe tener al menos 2 caracteres"
        
        # Validar color hexadecimal
        if not color.startswith("#") or len(color) != 7:
            return None, "El color debe estar en formato #RRGGBB"
        
        # Verificar nombre duplicado
        existing = db.query(Barber).filter(
            func.lower(Barber.name) == name.strip().lower()
        ).first()
        if existing:
            return None, f"Ya existe un barbero con el nombre '{name}'"
        
        barber = Barber(name=name.strip(), color=color.upper())
        db.add(barber)
        db.flush()
        return barber, None
    
    @staticmethod
    def update_barber(
        db: Session, 
        barber_id: int, 
        name: Optional[str] = None,
        color: Optional[str] = None
    ) -> Tuple[Optional[Barber], Optional[str]]:
        """
        Actualiza nombre y/o color de un barbero.
        
        Args:
            db: Sesión de base de datos
            barber_id: ID del barbero
            name: Nuevo nombre (opcional)
            color: Nuevo color (opcional)
            
        Retorna:
            Tupla (Barbero actualizado, mensaje de error)
        """
        barber = BarberService.get_barber_by_id(db, barber_id)
        if not barber:
            return None, "Barbero no encontrado"
        
        # Actualizar nombre si se proporciona
        if name is not None:
            if len(name.strip()) < 2:
                return None, "El nombre debe tener al menos 2 caracteres"
            
            # Verificar nombre duplicado (excepto el mismo barbero)
            existing = db.query(Barber).filter(
                func.lower(Barber.name) == name.strip().lower(),
                Barber.id != barber_id
            ).first()
            if existing:
                return None, f"Ya existe otro barbero con el nombre '{name}'"
            
            barber.name = name.strip()
        
        # Actualizar color si se proporciona
        if color is not None:
            if not color.startswith("#") or len(color) != 7:
                return None, "El color debe estar en formato #RRGGBB"
            barber.color = color.upper()
        
        db.flush()
        return barber, None
    
    @staticmethod
    def toggle_active(db: Session, barber_id: int) -> Tuple[Optional[Barber], Optional[str]]:
        """
        Activa o desactiva un barbero.
        
        Args:
            db: Sesión de base de datos
            barber_id: ID del barbero
            
        Retorna:
            Tupla (Barbero actualizado, mensaje de error)
        """
        barber = BarberService.get_barber_by_id(db, barber_id)
        if not barber:
            return None, "Barbero no encontrado"
        
        # Si se va a desactivar, validar
        if barber.is_active:
            can_deactivate, error = BarberService.can_deactivate(db, barber_id)
            if not can_deactivate:
                return None, error
        
        barber.is_active = not barber.is_active
        db.flush()
        return barber, None
    
    @staticmethod
    def can_deactivate(db: Session, barber_id: int) -> Tuple[bool, Optional[str]]:
        """
        Verifica si un barbero puede ser desactivado.
        
        Args:
            db: Sesión de base de datos
            barber_id: ID del barbero
            
        Retorna:
            Tupla (puede desactivar, mensaje de error)
        """
        # Verificar que no sea el último barbero activo
        active_count = db.query(Barber).filter(Barber.is_active == True).count()
        if active_count <= 1:
            return False, "Debe haber al menos un barbero activo"
        
        # Verificar citas futuras
        today = date.today()
        future_appointments = db.query(Appointment).filter(
            Appointment.barber_id == barber_id,
            func.date(Appointment.start_time) >= today,
            Appointment.status.in_(["pendiente", "confirmado"])
        ).count()
        
        if future_appointments > 0:
            return False, f"El barbero tiene {future_appointments} cita(s) futura(s) asignada(s)"
        
        return True, None
    
    @staticmethod
    def get_barber_stats(db: Session, barber_id: int, month: Optional[date] = None) -> dict:
        """
        Obtiene estadísticas de un barbero.
        
        Args:
            db: Sesión de base de datos
            barber_id: ID del barbero
            month: Mes para las estadísticas (por defecto mes actual)
            
        Retorna:
            Diccionario con estadísticas
        """
        if month is None:
            month = date.today()
        
        # Primer y último día del mes
        first_day = month.replace(day=1)
        if month.month == 12:
            last_day = month.replace(year=month.year + 1, month=1, day=1)
        else:
            last_day = month.replace(month=month.month + 1, day=1)
        
        # Contar citas del mes
        appointments = db.query(Appointment).filter(
            Appointment.barber_id == barber_id,
            Appointment.start_time >= first_day,
            Appointment.start_time < last_day
        ).all()
        
        total_appointments = len(appointments)
        completed = len([a for a in appointments if a.status == "completado"])
        cancelled = len([a for a in appointments if a.status == "cancelado"])
        
        return {
            "total_appointments": total_appointments,
            "completed": completed,
            "cancelled": cancelled,
            "pending": total_appointments - completed - cancelled
        }

