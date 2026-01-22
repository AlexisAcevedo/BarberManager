"""
Modelos ORM de SQLAlchemy para la aplicación Barber Manager.
Define las entidades Client, Service, Barber, User y Appointment.
"""
from datetime import datetime
from typing import Optional, List

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, 
    Text, DateTime, ForeignKey, create_engine, Index
)
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column


class Base(DeclarativeBase):
    """Clase base para todos los modelos ORM."""
    pass


class Barber(Base):
    """
    Entidad Barbero que representa un miembro del personal.
    """
    __tablename__ = "barbers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str] = mapped_column(String(20), default="#2196F3")  # Color de identidad en UI
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )
    
    # Relaciones
    user: Mapped[Optional["User"]] = relationship("User", back_populates="barber", uselist=False)
    appointments: Mapped[List["Appointment"]] = relationship("Appointment", back_populates="barber")
    
    def __repr__(self) -> str:
        return f"<Barber(id={self.id}, name='{self.name}')>"


class User(Base):
    """
    Entidad Usuario para autenticación.
    Vinculado a un Barbero (o puede ser un admin).
    Incluye campos para rate limiting de login.
    """
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="barber")  # admin, barber
    barber_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("barbers.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Campos para rate limiting
    failed_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Campo para forzar cambio de contraseña
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relaciones
    barber: Mapped[Optional["Barber"]] = relationship("Barber", back_populates="user")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"


class Client(Base):
    """
    Entidad Cliente que representa un cliente.
    Almacena información de contacto e historial de turnos.
    """
    __tablename__ = "clients"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )
    
    # Relación con turnos
    appointments: Mapped[List["Appointment"]] = relationship(
        "Appointment", back_populates="client", cascade="all, delete-orphan"
    )
    
    # Índices para optimizar búsquedas
    __table_args__ = (
        Index('idx_client_name', 'name'),
        Index('idx_client_phone', 'phone'),
    )
    
    def __repr__(self) -> str:
        return f"<Client(id={self.id}, name='{self.name}', email='{self.email}')>"


class Service(Base):
    """
    Entidad Servicio que representa un servicio ofrecido.
    Incluye información de duración y precio.
    """
    __tablename__ = "services"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)  # Duración en minutos
    price: Mapped[float] = mapped_column(Float, default=0.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relación con turnos
    appointments: Mapped[List["Appointment"]] = relationship(
        "Appointment", back_populates="service"
    )
    
    def __repr__(self) -> str:
        return f"<Service(id={self.id}, name='{self.name}', duration={self.duration}min)>"


class Appointment(Base):
    """
    Entidad Turno que representa una reserva programada.
    Vincula clientes con servicios, horarios y estado de sincronización.
    Incluye asignación de barbero.
    """
    __tablename__ = "appointments"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    client_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("clients.id"), nullable=False
    )
    service_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("services.id"), nullable=False
    )
    barber_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("barbers.id"), nullable=False
    )
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False
    )  # pending (pendiente), confirmed (confirmado), cancelled (cancelado)
    google_event_id: Mapped[Optional[str]] = mapped_column(
        String(255), unique=True, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )
    
    # Relaciones
    client: Mapped["Client"] = relationship("Client", back_populates="appointments")
    service: Mapped["Service"] = relationship("Service", back_populates="appointments")
    barber: Mapped["Barber"] = relationship("Barber", back_populates="appointments")
    
    # Índices para optimizar consultas por fecha y barbero
    __table_args__ = (
        Index('idx_appointment_start_time', 'start_time'),
        Index('idx_appointment_barber_date', 'barber_id', 'start_time'),
        Index('idx_appointment_status', 'status'),
    )
    
    def __repr__(self) -> str:
        return (
            f"<Appointment(id={self.id}, client_id={self.client_id}, "
            f"barber_id={self.barber_id}, start={self.start_time}, status='{self.status}')>"
        )


class Settings(Base):
    """
    Configuración de la aplicación almacenada en base de datos.
    Usa pares clave-valor para flexibilidad.
    """
    __tablename__ = "settings"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    
    def __repr__(self) -> str:
        return f"<Settings(key='{self.key}', value='{self.value}')>"
