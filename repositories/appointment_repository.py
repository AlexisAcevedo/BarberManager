"""
Repositorio de turnos para Barber Manager.
Optimizado para rendimiento usando carga anticipada (eager loading).
"""
from datetime import datetime, date
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from models.base import Appointment
from repositories.base_repository import BaseRepository


class AppointmentRepository(BaseRepository[Appointment]):
    """
    Repositorio para la entidad Turno.
    Optimizado para rendimiento usando carga anticipada.
    """
    def __init__(self):
        super().__init__(Appointment)

    def get_appointments_by_date(
        self, 
        db: Session, 
        target_date: date, 
        barber_id: Optional[int] = None
    ) -> List[Appointment]:
        """
        Obtiene turnos para una fecha específica con CARGA ANTICIPADA.
        SOLUCIONA EL PROBLEMA DE CONSULTAS N+1.
        
        Args:
            db: Sesión de base de datos
            target_date: Fecha objetivo
            barber_id: ID del barbero (opcional)
            
        Retorna:
            Lista de turnos para la fecha
        """
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())
        
        query = db.query(Appointment).options(
            joinedload(Appointment.client),
            joinedload(Appointment.service),
            joinedload(Appointment.barber)
        ).filter(
            Appointment.start_time >= start_of_day,
            Appointment.start_time <= end_of_day,
            Appointment.status != "cancelled"
        )
        
        if barber_id:
            query = query.filter(Appointment.barber_id == barber_id)
            
        return query.order_by(Appointment.start_time).all()

    def find_overlapping(
        self,
        db: Session,
        start_time: datetime,
        end_time: datetime,
        barber_id: int,
        exclude_id: Optional[int] = None
    ) -> List[Appointment]:
        """
        Encuentra turnos que se solapan con el rango de tiempo dado.
        
        Args:
            db: Sesión de base de datos
            start_time: Hora de inicio propuesta
            end_time: Hora de fin propuesta
            barber_id: ID del barbero
            exclude_id: ID de turno a excluir (opcional)
            
        Retorna:
            Lista de turnos que se solapan
        """
        query = db.query(Appointment).filter(
            Appointment.status != "cancelled",
            Appointment.barber_id == barber_id,
            Appointment.start_time < end_time,
            Appointment.end_time > start_time
        )
        
        if exclude_id:
            query = query.filter(Appointment.id != exclude_id)
            
        return query.all()

    def get_stats_by_period(self, db: Session, start_date: date, end_date: date) -> dict:
        """
        Obtiene estadísticas resumidas para un rango de fechas.
        
        Args:
            db: Sesión de base de datos
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
        Retorna:
            Diccionario con conteo total, ingresos y turnos
        """
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())
        
        appointments = db.query(Appointment).options(
            joinedload(Appointment.service)
        ).filter(
            Appointment.start_time >= start_dt,
            Appointment.start_time <= end_dt,
            Appointment.status != "cancelled"
        ).all()
        
        total_income = sum(app.service.price for app in appointments)
        total_count = len(appointments)
        
        return {
            "total_count": total_count,
            "total_income": total_income,
            "appointments": appointments
        }

    def get_stats_by_status(self, db: Session, start_date: date, end_date: date) -> dict:
        """
        Obtiene estadísticas resumidas agrupadas por estado del turno.
        
        Args:
            db: Sesión de base de datos
            start_date: Fecha de inicio
            end_date: Fecha de fin
            
        Retorna:
            Diccionario con estadísticas por estado (confirmed, pending, cancelled)
        """
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())
        
        appointments = db.query(Appointment).options(
            joinedload(Appointment.service)
        ).filter(
            Appointment.start_time >= start_dt,
            Appointment.start_time <= end_dt
        ).all()
        
        # Agrupar por estado
        confirmed = [a for a in appointments if a.status == "confirmed"]
        pending = [a for a in appointments if a.status == "pending"]
        cancelled = [a for a in appointments if a.status == "cancelled"]
        
        return {
            "confirmed": {
                "count": len(confirmed),
                "income": sum(a.service.price for a in confirmed)
            },
            "pending": {
                "count": len(pending),
                "income": sum(a.service.price for a in pending)
            },
            "cancelled": {
                "count": len(cancelled),
                "income": 0.0
            },
            "total": {
                "count": len(appointments),
                "income": sum(a.service.price for a in confirmed)  # Solo confirmados cuenta
            }
        }

    def get_barber_performance(self, db: Session, start_date: date, end_date: date, status: str = None) -> List[dict]:
        """
        Obtiene estadísticas por barbero.
        
        Args:
            db: Sesión de base de datos
            start_date: Fecha de inicio
            end_date: Fecha de fin
            status: Filtrar por estado específico (opcional)
            
        Retorna:
            Lista de diccionarios con nombre, conteo e ingresos por barbero
        """
        from sqlalchemy import func
        from models.base import Barber, Service
        
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())
        
        # Construir consulta
        query = db.query(
            Barber.name,
            func.count(Appointment.id).label("count"),
            func.sum(Service.price).label("income")
        ).join(Appointment, Appointment.barber_id == Barber.id)\
         .join(Service, Appointment.service_id == Service.id)\
         .filter(
            Appointment.start_time >= start_dt,
            Appointment.start_time <= end_dt
        )
        
        # Aplicar filtro de estado
        if status:
            query = query.filter(Appointment.status == status)
        else:
            query = query.filter(Appointment.status != "cancelled")
        
        results = query.group_by(Barber.id).all()
        
        return [{"name": r[0], "count": r[1], "income": r[2] or 0.0} for r in results]
