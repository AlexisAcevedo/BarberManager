"""
Repositorio base genérico para Barber Manager.
Proporciona operaciones CRUD comunes.
"""
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    Implementación base de repositorio con operaciones CRUD comunes.
    """
    def __init__(self, model: Type[T]):
        """
        Inicializa el repositorio con el modelo especificado.
        
        Args:
            model: Clase del modelo SQLAlchemy
        """
        self.model = model

    def get_by_id(self, db: Session, id: any) -> Optional[T]:
        """
        Obtiene un registro por su ID.
        
        Args:
            db: Sesión de base de datos
            id: ID del registro
            
        Retorna:
            Registro si se encuentra, None en caso contrario
        """
        return db.get(self.model, id)

    def get_all(self, db: Session) -> List[T]:
        """
        Obtiene todos los registros del modelo.
        
        Args:
            db: Sesión de base de datos
            
        Retorna:
            Lista de todos los registros
        """
        return db.query(self.model).all()

    def create(self, db: Session, obj_in: T) -> T:
        """
        Crea un nuevo registro.
        
        Args:
            db: Sesión de base de datos
            obj_in: Objeto a crear
            
        Retorna:
            Objeto creado
        """
        db.add(obj_in)
        db.flush()
        return obj_in

    def delete(self, db: Session, id: any) -> bool:
        """
        Elimina un registro por ID.
        
        Args:
            db: Sesión de base de datos
            id: ID del registro a eliminar
            
        Retorna:
            True si se eliminó, False si no se encontró
        """
        obj = self.get_by_id(db, id)
        if obj:
            db.delete(obj)
            return True
        return False
