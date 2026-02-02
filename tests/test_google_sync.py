
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from services.appointment_service import AppointmentService
from services.google_calendar_service import GoogleCalendarService
from services.settings_service import SettingsService
from models.base import Appointment, Client, Service

@pytest.fixture
def mock_google_service():
    with patch('services.appointment_service.google_calendar_service') as mock:
        yield mock

def test_sync_pending_appointments_disabled(db_session):
    """Test that nothing syncs if feature is disabled."""
    SettingsService.set_google_calendar_enabled(db_session, False)
    
    success, fail = AppointmentService.sync_pending_appointments(db_session)
    
    assert success == 0
    assert fail == 0

def test_sync_pending_appointments_success(db_session, sample_client, sample_service, sample_barber, mock_google_service):
    """Test syncing pending appointments successfully."""
    # Enable sync
    SettingsService.set_google_calendar_enabled(db_session, True)
    
    # Create a future appointment (without google_event_id by default)
    future_time = datetime.now() + timedelta(days=1)
    appt = Appointment(
        client_id=sample_client.id,
        service_id=sample_service.id,
        barber_id=sample_barber.id,
        start_time=future_time,
        end_time=future_time + timedelta(minutes=30),
        status="confirmed"
    )
    db_session.add(appt)
    db_session.commit()
    
    # Mock successful creation
    mock_google_service.create_event.return_value = "gooogle_event_123"
    
    success, fail = AppointmentService.sync_pending_appointments(db_session)
    
    assert success == 1
    assert fail == 0
    
    # Verify DB was updated
    db_session.refresh(appt)
    assert appt.google_event_id == "gooogle_event_123"

def test_sync_pending_appointments_failure(db_session, sample_client, sample_service, sample_barber, mock_google_service):
    """Test handling of sync failure."""
    # Enable sync
    SettingsService.set_google_calendar_enabled(db_session, True)
    
    # Create appointment
    future_time = datetime.now() + timedelta(days=2)
    appt = Appointment(
        client_id=sample_client.id,
        service_id=sample_service.id,
        barber_id=sample_barber.id,
        start_time=future_time,
        end_time=future_time + timedelta(minutes=30),
        status="confirmed"
    )
    db_session.add(appt)
    db_session.commit()
    
    # Mock failure
    mock_google_service.create_event.return_value = None
    
    success, fail = AppointmentService.sync_pending_appointments(db_session)
    
    assert success == 0
    assert fail == 1
    
    # Verify DB was NOT updated
    db_session.refresh(appt)
    assert appt.google_event_id is None
