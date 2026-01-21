"""
Tests para el repositorio de turnos.
"""
import pytest
from datetime import date, datetime, timedelta
from models.base import Appointment, Client, Service, Barber
from repositories.appointment_repository import AppointmentRepository


class TestAppointmentRepository:
    """Tests para AppointmentRepository."""
    
    @pytest.fixture
    def setup_data(self, db_session):
        """Prepara datos de prueba."""
        # Crear barbero
        barber = Barber(name="Test Barber", color="#FF0000")
        db_session.add(barber)
        
        # Crear cliente
        client = Client(name="Test Client", email="client@test.com")
        db_session.add(client)
        
        # Crear servicio
        service = Service(name="Test Service", duration=30, price=100.0)
        db_session.add(service)
        
        db_session.flush()
        
        return {"barber": barber, "client": client, "service": service}
    
    def test_get_appointments_by_date_empty(self, db_session):
        """Test obtener turnos de un día sin turnos."""
        repo = AppointmentRepository()
        appointments = repo.get_appointments_by_date(
            db_session, 
            date.today() + timedelta(days=100)
        )
        assert appointments == []
    
    def test_get_appointments_by_date_with_data(self, db_session, setup_data):
        """Test obtener turnos de un día con datos."""
        repo = AppointmentRepository()
        
        # Crear turno
        today = date.today()
        start = datetime.combine(today, datetime.min.time().replace(hour=14))
        end = start + timedelta(minutes=30)
        
        appt = Appointment(
            client_id=setup_data["client"].id,
            service_id=setup_data["service"].id,
            barber_id=setup_data["barber"].id,
            start_time=start,
            end_time=end,
            status="pending"
        )
        db_session.add(appt)
        db_session.commit()
        
        appointments = repo.get_appointments_by_date(db_session, today)
        assert len(appointments) >= 1
    
    def test_find_overlapping(self, db_session, setup_data):
        """Test encontrar turnos solapados."""
        repo = AppointmentRepository()
        
        today = date.today()
        start = datetime.combine(today, datetime.min.time().replace(hour=15))
        end = start + timedelta(minutes=30)
        
        # Crear turno existente
        appt = Appointment(
            client_id=setup_data["client"].id,
            service_id=setup_data["service"].id,
            barber_id=setup_data["barber"].id,
            start_time=start,
            end_time=end,
            status="pending"
        )
        db_session.add(appt)
        db_session.commit()
        
        # Buscar solapamiento en el mismo horario
        overlapping = repo.find_overlapping(
            db_session,
            start,
            end,
            setup_data["barber"].id
        )
        assert len(overlapping) == 1
    
    def test_get_stats_by_status(self, db_session, setup_data):
        """Test obtener estadísticas por estado."""
        repo = AppointmentRepository()
        
        today = date.today()
        start = datetime.combine(today, datetime.min.time().replace(hour=16))
        
        # Crear turno confirmado
        appt = Appointment(
            client_id=setup_data["client"].id,
            service_id=setup_data["service"].id,
            barber_id=setup_data["barber"].id,
            start_time=start,
            end_time=start + timedelta(minutes=30),
            status="confirmed"
        )
        db_session.add(appt)
        db_session.commit()
        
        stats = repo.get_stats_by_status(db_session, today, today)
        
        assert "confirmed" in stats
        assert "pending" in stats
        assert "cancelled" in stats
        assert stats["confirmed"]["count"] >= 1
