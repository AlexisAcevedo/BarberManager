"""
Servicio de clientes para Barber Manager.
Maneja operaciones CRUD de clientes y funcionalidad de búsqueda.
"""
import re
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from models.base import Client
from utils.validators import validate_email, validate_phone, validate_name


class ClientService:
    """
    Capa de servicio para gestión de clientes.
    Encapsula toda la lógica de negocio relacionada con clientes.
    """
    
    @classmethod
    def get_all_clients(cls, db: Session) -> List[Client]:
        """
        Obtiene todos los clientes ordenados por nombre.
        
        Args:
            db: Sesión de base de datos
            
        Retorna:
            Lista de todos los clientes
        """
        return db.query(Client).order_by(Client.name).all()
    
    @classmethod
    def get_client_by_id(cls, db: Session, client_id: int) -> Optional[Client]:
        """
        Obtiene un cliente por su ID.
        
        Args:
            db: Sesión de base de datos
            client_id: ID del cliente
            
        Retorna:
            Cliente si se encuentra, None en caso contrario
        """
        return db.query(Client).filter(Client.id == client_id).first()
    
    @classmethod
    def search_clients(
        cls, 
        db: Session, 
        search_term: str
    ) -> List[Client]:
        """
        Busca clientes por nombre o número de teléfono.
        
        Args:
            db: Sesión de base de datos
            search_term: Cadena de búsqueda
            
        Retorna:
            Lista de clientes que coinciden
        """
        if not search_term:
            return []
        
        # Sanitizar entrada para prevenir inyección SQL
        from utils.validators import sanitize_string
        search_term = sanitize_string(search_term)
        if not search_term:
            return []
        
        # Escapar caracteres especiales de SQL LIKE
        search_term = re.sub(r'[%_\\]', '', search_term)
        search_pattern = f"%{search_term}%"
        
        return (
            db.query(Client)
            .filter(
                (Client.name.ilike(search_pattern)) |
                (Client.phone.ilike(search_pattern))
            )
            .order_by(Client.name)
            .limit(10)
            .all()
        )
    
    @classmethod
    def create_client(
        cls,
        db: Session,
        name: str,
        email: str,
        phone: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Tuple[Optional[Client], Optional[str]]:
        """
        Crea un nuevo cliente.
        
        Args:
            db: Sesión de base de datos
            name: Nombre del cliente
            email: Email del cliente (requerido para invitaciones de Google)
            phone: Número de teléfono del cliente
            notes: Notas adicionales
            
        Retorna:
            Tupla de (cliente, mensaje_de_error)
        """
        # Validar nombre
        is_valid, error = validate_name(name)
        if not is_valid:
            return None, error
        
        # Validar email
        is_valid, error = validate_email(email)
        if not is_valid:
            return None, error
        
        # Validar teléfono (opcional)
        is_valid, error = validate_phone(phone)
        if not is_valid:
            return None, error
        
        # Verificar email duplicado
        existing = db.query(Client).filter(Client.email == email.strip()).first()
        if existing:
            return None, "Ya existe un cliente con ese email"
        
        # Crear cliente
        client = Client(
            name=name.strip(),
            email=email.strip(),
            phone=phone.strip() if phone else None,
            notes=notes.strip() if notes else None
        )
        
        db.add(client)
        db.flush()
        
        return client, None
    
    @classmethod
    def update_client(
        cls,
        db: Session,
        client_id: int,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Tuple[Optional[Client], Optional[str]]:
        """
        Actualiza un cliente existente.
        
        Args:
            db: Sesión de base de datos
            client_id: ID del cliente a actualizar
            name: Nuevo nombre (si se cambia)
            email: Nuevo email (si se cambia)
            phone: Nuevo teléfono (si se cambia)
            notes: Nuevas notas (si se cambian)
            
        Retorna:
            Tupla de (cliente, mensaje_de_error)
        """
        client = db.query(Client).filter(Client.id == client_id).first()
        
        if not client:
            return None, "Cliente no encontrado"
        
        # Actualizar campos si se proporcionan
        if name is not None:
            if not name.strip():
                return None, "El nombre no puede estar vacío"
            client.name = name.strip()
        
        if email is not None:
            if not email.strip():
                return None, "El email no puede estar vacío"
            # Verificar email duplicado (excluyendo cliente actual)
            existing = db.query(Client).filter(
                Client.email == email,
                Client.id != client_id
            ).first()
            if existing:
                return None, "Ya existe otro cliente con ese email"
            client.email = email.strip()
        
        if phone is not None:
            client.phone = phone.strip() if phone else None
        
        if notes is not None:
            client.notes = notes.strip() if notes else None
        
        return client, None
    
    @classmethod
    def delete_client(
        cls,
        db: Session,
        client_id: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Elimina un cliente.
        
        Args:
            db: Sesión de base de datos
            client_id: ID del cliente a eliminar
            
        Retorna:
            Tupla de (éxito, mensaje_de_error)
        """
        client = db.query(Client).filter(Client.id == client_id).first()
        
        if not client:
            return False, "Cliente no encontrado"
        
        # Verificar turnos existentes
        if client.appointments:
            return False, "No se puede eliminar un cliente con turnos asociados"
        
        db.delete(client)
        return True, None
