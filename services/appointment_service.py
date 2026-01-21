"""
Appointment service for Barber Manager.
Handles appointment CRUD, conflict detection, and Google Calendar sync.
"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from database import get_db
from models.base import Appointment, Service, Client
from services.settings_service import SettingsService
from repositories.appointment_repository import AppointmentRepository

appointment_repo = AppointmentRepository()


class AppointmentService:
    """
    Service layer for appointment management.
    Encapsulates all business logic related to appointments.
    """
    
    # Default business hours (fallback if settings not available)
    DEFAULT_START_HOUR = 12
    DEFAULT_END_HOUR = 20
    SLOT_INTERVAL_MINUTES = 15
    
    @classmethod
    def get_business_hours(cls, db: Session) -> Tuple[int, int]:
        """
        Get business hours from settings.
        
        Args:
            db: Database session
            
        Returns:
            Tuple of (start_hour, end_hour)
        """
        return SettingsService.get_business_hours(db)
    
    @classmethod
    def get_all_time_slots(cls, db: Session = None) -> List[Tuple[int, int]]:
        """
        Generate all possible time slots for a day.
        
        Args:
            db: Database session (optional, uses default hours if not provided)
        
        Returns:
            List of tuples (hour, minute) for each 15-minute interval
        """
        if db:
            start_hour, end_hour = cls.get_business_hours(db)
        else:
            start_hour, end_hour = cls.DEFAULT_START_HOUR, cls.DEFAULT_END_HOUR
        
        slots = []
        for hour in range(start_hour, end_hour):
            for minute in range(0, 60, cls.SLOT_INTERVAL_MINUTES):
                slots.append((hour, minute))
        return slots
    
    @classmethod
    def get_appointments_for_date(
        cls, 
        db: Session, 
        target_date: date,
        barber_id: Optional[int] = None
    ) -> List[Appointment]:
        """
        Get all appointments for a specific date.
        
        Args:
            db: Database session
            target_date: The date to query
            
        Returns:
            List of appointments for that date
        """
        return appointment_repo.get_appointments_by_date(db, target_date, barber_id=barber_id)
    
    @classmethod
    def get_available_slots(
        cls,
        db: Session,
        target_date: date,
        service_duration: int,
        barber_id: int
    ) -> List[Tuple[int, int, bool]]:
        """
        Get all time slots with availability status for a given date and service.
        
        This is the CRITICAL conflict detection logic:
        For each slot, checks if booking a service of the given duration
        would overlap with any existing appointment.
        
        Args:
            db: Database session
            target_date: The date to check
            service_duration: Duration of the selected service in minutes
            
        Returns:
            List of tuples (hour, minute, is_available)
        """
        # Get existing appointments for the date and barber
        existing_appointments = cls.get_appointments_for_date(db, target_date, barber_id=barber_id)
        
        # Generate all possible slots with availability (uses dynamic business hours)
        all_slots = cls.get_all_time_slots(db)
        
        # Get dynamic end hour for validation
        _, end_hour = cls.get_business_hours(db)
        
        result = []
        
        for hour, minute in all_slots:
            # Calculate potential start and end times
            slot_start = datetime.combine(
                target_date, 
                datetime.min.time().replace(hour=hour, minute=minute)
            )
            slot_end = slot_start + timedelta(minutes=service_duration)
            
            # Check if this slot would exceed business hours
            business_end = datetime.combine(
                target_date,
                datetime.min.time().replace(hour=end_hour, minute=0)
            )
            
            if slot_end > business_end:
                result.append((hour, minute, False))
                continue
            
            # Check for overlap with existing appointments
            is_available = True
            for appt in existing_appointments:
                # Overlap occurs if:
                # existing.start < potential.end AND existing.end > potential.start
                if appt.start_time < slot_end and appt.end_time > slot_start:
                    is_available = False
                    break
            
            result.append((hour, minute, is_available))
        
        return result
    
    @classmethod
    def check_slot_availability(
        cls,
        db: Session,
        start_time: datetime,
        end_time: datetime,
        barber_id: int,
        exclude_appointment_id: Optional[int] = None
    ) -> bool:
        """
        Check if a specific time slot is available.
        
        Args:
            db: Database session
            start_time: Proposed start time
            end_time: Proposed end time
            exclude_appointment_id: Optional appointment ID to exclude (for updates)
            
        Returns:
            True if slot is available, False otherwise
        """
        overlapping = appointment_repo.find_overlapping(
            db, start_time, end_time, barber_id, exclude_appointment_id
        )
        return len(overlapping) == 0
    
    @classmethod
    def create_appointment(
        cls,
        db: Session,
        client_id: int,
        service_id: int,
        barber_id: int,
        start_time: datetime,
        sync_to_google: bool = True
    ) -> Tuple[Optional[Appointment], Optional[str]]:
        """
        Create a new appointment with conflict checking.
        
        Args:
            db: Database session
            client_id: ID of the client
            service_id: ID of the service
            start_time: Start datetime of the appointment
            sync_to_google: Whether to sync to Google Calendar
            
        Returns:
            Tuple of (appointment, error_message)
            appointment is None if creation failed
        """
        # Get service to calculate end time
        service = db.query(Service).filter(Service.id == service_id).first()
        if not service:
            return None, "Servicio no encontrado"
        
        # Get client for validation
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            return None, "Cliente no encontrado"
        
        # Calculate end time
        end_time = start_time + timedelta(minutes=service.duration)
        
        # Check availability
        if not cls.check_slot_availability(db, start_time, end_time, barber_id):
            return None, "El horario seleccionado no está disponible para este barbero"
        
        # Create appointment
        appointment = Appointment(
            client_id=client_id,
            service_id=service_id,
            barber_id=barber_id,
            start_time=start_time,
            end_time=end_time,
            status="pending"
        )
        
        db.add(appointment)
        db.flush()  # Get the ID without committing
        
        # Sync to Google Calendar
        if sync_to_google:
            google_event_id = cls.sync_to_google(appointment, client, service)
            if google_event_id:
                appointment.google_event_id = google_event_id
        
        return appointment, None
    
    @classmethod
    def update_appointment_status(
        cls,
        db: Session,
        appointment_id: int,
        new_status: str
    ) -> Tuple[Optional[Appointment], Optional[str]]:
        """
        Update the status of an appointment.
        
        Args:
            db: Database session
            appointment_id: ID of the appointment
            new_status: New status (pending, confirmed, cancelled)
            
        Returns:
            Tuple of (appointment, error_message)
        """
        valid_statuses = ["pending", "confirmed", "cancelled"]
        if new_status not in valid_statuses:
            return None, f"Estado inválido. Use: {', '.join(valid_statuses)}"
        
        appointment = db.query(Appointment).filter(
            Appointment.id == appointment_id
        ).first()
        
        if not appointment:
            return None, "Turno no encontrado"
        
        appointment.status = new_status
        return appointment, None
    
    @classmethod
    def get_appointment_by_id(
        cls,
        db: Session,
        appointment_id: int
    ) -> Optional[Appointment]:
        """Get a single appointment by ID."""
        return db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    @classmethod
    def delete_appointment(
        cls,
        db: Session,
        appointment_id: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Delete an appointment.
        
        Args:
            db: Database session
            appointment_id: ID of the appointment to delete
            
        Returns:
            Tuple of (success, error_message)
        """
        return appointment_repo.delete(db, appointment_id)
    
    @staticmethod
    def sync_to_google(
        appointment: Appointment,
        client: Client,
        service: Service
    ) -> Optional[str]:
        """
        Sync appointment to Google Calendar.
        
        This is a placeholder method that simulates the Google Calendar API call.
        In production, this would use google-api-python-client.
        
        Args:
            appointment: The appointment to sync
            client: The client associated with the appointment
            service: The service for the appointment
            
        Returns:
            Google event ID if successful, None otherwise
        """
        # Placeholder: Print sync information to console
        print("=" * 50)
        print("📅 GOOGLE CALENDAR SYNC (Placeholder)")
        print("=" * 50)
        print(f"  Client: {client.name} ({client.email})")
        print(f"  Service: {service.name} ({service.duration} min)")
        print(f"  Start: {appointment.start_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"  End: {appointment.end_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"  Status: {appointment.status}")
        print("=" * 50)
        
        # Generate a mock event ID
        mock_event_id = f"google_event_{appointment.id}_{int(datetime.now().timestamp())}"
        print(f"  ✓ Mock Event ID: {mock_event_id}")
        print()
        
        return mock_event_id
    
    @classmethod
    def get_daily_schedule(
        cls,
        db: Session,
        target_date: date,
        barber_id: Optional[int] = None
    ) -> List[dict]:
        """
        Get a complete daily schedule including appointments and free slots.
        
        Args:
            db: Database session
            target_date: The date to get schedule for
            
        Returns:
            List of schedule items (appointments and free slots)
        """
        appointments = cls.get_appointments_for_date(db, target_date, barber_id=barber_id)
        all_slots = cls.get_all_time_slots(db)  # Use dynamic business hours
        
        schedule = []
        appt_index = 0
        
        for hour, minute in all_slots:
            slot_time = datetime.combine(
                target_date,
                datetime.min.time().replace(hour=hour, minute=minute)
            )
            
            # Check if there's an appointment at this slot
            if appt_index < len(appointments):
                appt = appointments[appt_index]
                if appt.start_time == slot_time:
                    # Serialize data to avoid detached instance errors
                    schedule.append({
                        "type": "appointment",
                        "time": slot_time,
                        "appointment": {
                            "id": appt.id,
                            "start_time": appt.start_time,
                            "end_time": appt.end_time,
                            "status": appt.status
                        },
                        "client": {
                            "id": appt.client.id,
                            "name": appt.client.name,
                            "phone": appt.client.phone,
                            "email": appt.client.email
                        },
                        "service": {
                            "id": appt.service.id,
                            "name": appt.service.name,
                            "duration": appt.service.duration
                        }
                    })
                    appt_index += 1
                    continue
            
            # Check if this slot is within an existing appointment
            is_occupied = False
            for appt in appointments:
                if appt.start_time <= slot_time < appt.end_time:
                    is_occupied = True
                    break
            
            if not is_occupied:
                schedule.append({
                    "type": "free",
                    "time": slot_time
                })
        
        return schedule

