"""
Unit tests for AppointmentService dynamic business hours logic.
"""
import pytest
from datetime import date, datetime
from services.appointment_service import AppointmentService
from services.settings_service import SettingsService

def test_get_all_time_slots_default(db_session):
    """Test time slots with default business hours (12-20)."""
    # 8 hours * 4 slots per hour = 32 slots
    slots = AppointmentService.get_all_time_slots(db_session)
    assert len(slots) == 32
    assert slots[0] == (12, 0)
    assert slots[-1] == (19, 45)

def test_get_all_time_slots_custom(db_session):
    """Test time slots with custom business hours (8-10)."""
    SettingsService.set_business_hours(db_session, 8, 10)
    db_session.commit()
    
    # 2 hours * 4 slots per hour = 8 slots
    slots = AppointmentService.get_all_time_slots(db_session)
    assert len(slots) == 8
    assert slots[0] == (8, 0)
    assert slots[-1] == (9, 45)

def test_get_available_slots_respects_business_end(db_session, sample_service, sample_barber):
    """Test that available slots do not exceed business hours."""
    # Set hours 10-12
    SettingsService.set_business_hours(db_session, 10, 12)
    db_session.commit()
    
    # Service duration 30 min
    target_date = date.today()
    slots = AppointmentService.get_available_slots(db_session, target_date, 30, barber_id=sample_barber.id)
    
    # Slots: 10:00, 10:15, 10:30, 10:45, 11:00, 11:15, 11:30, 11:45
    # 11:45 + 30m = 12:15 (Out of bounds)
    # 11:30 + 30m = 12:00 (OK)
    
    # Slot 11:30 should be available, 11:45 should not
    slot_11_30 = next(s for s in slots if s[0] == 11 and s[1] == 30)
    slot_11_45 = next(s for s in slots if s[0] == 11 and s[1] == 45)
    
    assert slot_11_30[2] is True
    assert slot_11_45[2] is False

def test_get_daily_schedule_custom_hours(db_session, sample_barber):
    """Test that daily schedule reflects custom hours."""
    SettingsService.set_business_hours(db_session, 15, 17)
    db_session.commit()
    
    schedule = AppointmentService.get_daily_schedule(db_session, date.today(), barber_id=sample_barber.id)
    # 2 hours * 4 slots = 8 items
    assert len(schedule) == 8
    assert schedule[0]["time"].hour == 15
    assert schedule[-1]["time"].hour == 16
    assert schedule[-1]["time"].minute == 45

def test_multi_barber_collision_avoidance(db_session, sample_client, sample_service):
    """Test that two different barbers can have appointments at the same time."""
    from models.base import Barber
    b1 = Barber(name="Barber 1")
    b2 = Barber(name="Barber 2")
    db_session.add_all([b1, b2])
    db_session.commit()
    
    start_time = datetime.combine(date.today(), datetime.min.time().replace(hour=12))
    
    # Create appointment for B1
    app1, err1 = AppointmentService.create_appointment(db_session, sample_client.id, sample_service.id, b1.id, start_time)
    assert err1 is None
    
    # Create appointment for B2 at same time (should be allowed)
    app2, err2 = AppointmentService.create_appointment(db_session, sample_client.id, sample_service.id, b2.id, start_time)
    assert err2 is None
    assert app1.id != app2.id
