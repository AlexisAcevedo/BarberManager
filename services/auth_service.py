"""
Servicio de autenticación para Barber Manager.
Maneja el hash de contraseñas, validación y simulación de sesión.
"""
import bcrypt
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from models.base import User, Barber


class AuthService:
    """
    Capa de servicio para autenticación y gestión de usuarios.
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """Genera un hash de la contraseña para almacenamiento seguro."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verifica una contraseña contra su hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    @classmethod
    def create_user(
        cls, 
        db: Session, 
        username: str, 
        password: str, 
        role: str = "barber", 
        barber_id: Optional[int] = None
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Crea un nuevo usuario con contraseña hasheada.
        
        Args:
            db: Sesión de base de datos
            username: Nombre de usuario
            password: Contraseña en texto plano
            role: Rol del usuario (admin o barber)
            barber_id: ID del barbero asociado (opcional)
            
        Retorna:
            Tupla de (usuario, mensaje_de_error)
        """
        # Verificar si el usuario ya existe
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            return None, "El nombre de usuario ya existe"

        user = User(
            username=username,
            password_hash=cls.hash_password(password),
            role=role,
            barber_id=barber_id
        )
        db.add(user)
        db.flush()
        return user, None

    @classmethod
    def authenticate(cls, db: Session, username: str, password: str) -> Optional[User]:
        """
        Autentica un usuario y retorna el objeto usuario si es exitoso.
        
        Args:
            db: Sesión de base de datos
            username: Nombre de usuario
            password: Contraseña
            
        Retorna:
            Usuario si la autenticación es exitosa, None en caso contrario
        """
        user = db.query(User).filter(User.username == username, User.is_active == True).first()
        if user and cls.verify_password(password, user.password_hash):
            return user
        return None
