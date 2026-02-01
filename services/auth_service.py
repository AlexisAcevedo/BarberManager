"""
Servicio de autenticación para Barber Manager.
Maneja el hash de contraseñas, validación, rate limiting y sesión.
"""
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from models.base import User, Barber
from config import logger


# Configuración de rate limiting
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 5


class AuthService:
    """
    Capa de servicio para autenticación y gestión de usuarios.
    Incluye protección contra ataques de fuerza bruta.
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
    def _is_locked(cls, user: User) -> bool:
        """
        Verifica si el usuario está bloqueado por intentos fallidos.
        
        Args:
            user: Usuario a verificar
            
        Retorna:
            True si está bloqueado, False en caso contrario
        """
        if user.locked_until and user.locked_until > datetime.now():
            return True
        return False
    
    @classmethod
    def _reset_failed_attempts(cls, db: Session, user: User) -> None:
        """Resetea los intentos fallidos y el bloqueo."""
        user.failed_attempts = 0
        user.locked_until = None
        db.flush()
    
    @classmethod
    def _increment_failed_attempts(cls, db: Session, user: User) -> None:
        """
        Incrementa los intentos fallidos y bloquea si excede el límite.
        """
        user.failed_attempts = (user.failed_attempts or 0) + 1
        
        if user.failed_attempts >= MAX_FAILED_ATTEMPTS:
            user.locked_until = datetime.now() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            logger.warning(f"Usuario {user.username} bloqueado por {LOCKOUT_DURATION_MINUTES} minutos")
        
        db.flush()

    @staticmethod
    def _validate_password(password: str) -> Optional[str]:
        """
        Valida que la contraseña cumpla los requisitos de seguridad.
        Requisito: Mínimo 8 caracteres.
        """
        if len(password) < 8:
            return "La contraseña debe tener al menos 8 caracteres"
        return None

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
        # Validar contraseña
        pwd_error = cls._validate_password(password)
        if pwd_error:
            return None, pwd_error

        # Verificar si el usuario ya existe
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            return None, "El nombre de usuario ya existe"

        user = User(
            username=username,
            password_hash=cls.hash_password(password),
            role=role,
            barber_id=barber_id,
            failed_attempts=0,
            locked_until=None
        )
        db.add(user)
        db.flush()
        return user, None

    @classmethod
    def authenticate(cls, db: Session, username: str, password: str) -> Tuple[Optional[User], Optional[str]]:
        """
        Autentica un usuario con protección de rate limiting.
        
        Args:
            db: Sesión de base de datos
            username: Nombre de usuario
            password: Contraseña
            
        Retorna:
            Tupla de (Usuario, mensaje_de_error)
            - Si éxito: (User, None)
            - Si falla: (None, mensaje)
        """
        user = db.query(User).filter(User.username == username, User.is_active == True).first()
        
        if not user:
            logger.info(f"Intento de login con usuario inexistente: {username}")
            return None, "Credenciales inválidas"
        
        # Verificar si está bloqueado
        if cls._is_locked(user):
            remaining = (user.locked_until - datetime.now()).seconds // 60 + 1
            logger.warning(f"Intento de login en cuenta bloqueada: {username}")
            return None, f"Cuenta bloqueada. Intente en {remaining} minutos"
        
        # Verificar contraseña
        if cls.verify_password(password, user.password_hash):
            # Login exitoso - resetear intentos
            cls._reset_failed_attempts(db, user)
            logger.info(f"Login exitoso: {username}")
            return user, None
        else:
            # Login fallido - incrementar intentos
            cls._increment_failed_attempts(db, user)
            attempts_left = MAX_FAILED_ATTEMPTS - user.failed_attempts
            
            if attempts_left > 0:
                return None, f"Credenciales inválidas. {attempts_left} intentos restantes"
            else:
                return None, f"Cuenta bloqueada por {LOCKOUT_DURATION_MINUTES} minutos"
    
    @classmethod
    def unlock_user(cls, db: Session, username: str) -> bool:
        """
        Desbloquea manualmente un usuario (para admins).
        
        Args:
            db: Sesión de base de datos
            username: Nombre de usuario a desbloquear
            
        Retorna:
            True si se desbloqueó, False si no se encontró
        """
        user = db.query(User).filter(User.username == username).first()
        if user:
            cls._reset_failed_attempts(db, user)
            logger.info(f"Usuario {username} desbloqueado manualmente")
            return True
        return False
    
    @classmethod
    def change_password(
        cls, 
        db: Session, 
        user_id: int, 
        new_password: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Cambia la contraseña de un usuario.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            new_password: Nueva contraseña
            
        Retorna:
            Tupla de (éxito, mensaje_de_error)
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False, "Usuario no encontrado"
        
        # Validar contraseña
        pwd_error = cls._validate_password(new_password)
        if pwd_error:
            return False, pwd_error
        
        user.password_hash = cls.hash_password(new_password)
        user.must_change_password = False
        db.flush()
        
        logger.info(f"Contraseña cambiada para usuario {user.username}")
        return True, None
