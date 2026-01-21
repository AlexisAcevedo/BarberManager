"""
Servicio de servicios para Barber Manager.
Maneja operaciones CRUD de servicios de barbería.
"""
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from models.base import Service


class ServiceService:
    """
    Capa de servicio para gestión de servicios de barbería.
    Encapsula toda la lógica de negocio relacionada con servicios.
    """
    
    @classmethod
    def get_all_services(cls, db: Session, active_only: bool = True) -> List[Service]:
        """
        Obtiene todos los servicios.
        
        Args:
            db: Sesión de base de datos
            active_only: Si es True, solo retorna servicios activos
            
        Retorna:
            Lista de servicios
        """
        query = db.query(Service).order_by(Service.name)
        if active_only:
            query = query.filter(Service.is_active == True)
        return query.all()
    
    @classmethod
    def get_service_by_id(cls, db: Session, service_id: int) -> Optional[Service]:
        """
        Obtiene un servicio por ID.
        
        Args:
            db: Sesión de base de datos
            service_id: ID del servicio
            
        Retorna:
            Servicio si se encuentra, None en caso contrario
        """
        return db.query(Service).filter(Service.id == service_id).first()
    
    @classmethod
    def create_service(
        cls,
        db: Session,
        name: str,
        duration: int,
        price: float = 0.0,
        is_active: bool = True
    ) -> Tuple[Optional[Service], Optional[str]]:
        """
        Crea un nuevo servicio.
        
        Args:
            db: Sesión de base de datos
            name: Nombre del servicio
            duration: Duración en minutos
            price: Precio del servicio
            is_active: Si el servicio está activo
            
        Retorna:
            Tupla de (servicio, mensaje_de_error)
        """
        # Validar campos requeridos
        if not name or not name.strip():
            return None, "El nombre es requerido"
        
        if duration <= 0:
            return None, "La duración debe ser mayor a 0"
        
        # Verificar nombre duplicado
        existing = db.query(Service).filter(Service.name == name.strip()).first()
        if existing:
            return None, "Ya existe un servicio con ese nombre"
        
        # Crear servicio
        service = Service(
            name=name.strip(),
            duration=duration,
            price=price,
            is_active=is_active
        )
        
        db.add(service)
        db.flush()
        
        return service, None
    
    @classmethod
    def update_service(
        cls,
        db: Session,
        service_id: int,
        name: Optional[str] = None,
        duration: Optional[int] = None,
        price: Optional[float] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[Optional[Service], Optional[str]]:
        """
        Actualiza un servicio existente.
        
        Args:
            db: Sesión de base de datos
            service_id: ID del servicio a actualizar
            name: Nuevo nombre (si se cambia)
            duration: Nueva duración (si se cambia)
            price: Nuevo precio (si se cambia)
            is_active: Nuevo estado activo (si se cambia)
            
        Retorna:
            Tupla de (servicio, mensaje_de_error)
        """
        service = db.query(Service).filter(Service.id == service_id).first()
        
        if not service:
            return None, "Servicio no encontrado"
        
        if name is not None:
            if not name.strip():
                return None, "El nombre no puede estar vacío"
            # Verificar nombre duplicado (excluyendo actual)
            existing = db.query(Service).filter(
                Service.name == name.strip(),
                Service.id != service_id
            ).first()
            if existing:
                return None, "Ya existe otro servicio con ese nombre"
            service.name = name.strip()
        
        if duration is not None:
            if duration <= 0:
                return None, "La duración debe ser mayor a 0"
            service.duration = duration
        
        if price is not None:
            service.price = price
        
        if is_active is not None:
            service.is_active = is_active
        
        return service, None
    
    @classmethod
    def delete_service(
        cls,
        db: Session,
        service_id: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Elimina un servicio.
        
        Args:
            db: Sesión de base de datos
            service_id: ID del servicio a eliminar
            
        Retorna:
            Tupla de (éxito, mensaje_de_error)
        """
        service = db.query(Service).filter(Service.id == service_id).first()
        
        if not service:
            return False, "Servicio no encontrado"
        
        # Verificar turnos existentes
        if service.appointments:
            return False, "No se puede eliminar un servicio con turnos asociados"
        
        db.delete(service)
        return True, None
