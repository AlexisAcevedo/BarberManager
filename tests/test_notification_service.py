"""
Unit tests for NotificationService.
"""
import pytest
from services.notification_service import NotificationService
from models.base import Appointment, Client, Service, Barber
from datetime import datetime

def test_generate_reminder_message():
    """Test reminder message generation."""
    # Mock objects (simplified)
    class MockClient:
        name = "Juan"
    class MockService:
        name = "Corte"
    class MockAppt:
        client = MockClient()
        service = MockService()
        start_time = datetime(2026, 1, 25, 15, 30)
    
    msg = NotificationService.generate_reminder_message(MockAppt())
    assert "Juan" in msg
    assert "15:30" in msg
    assert "25/01" in msg
    assert "Corte" in msg

def test_get_whatsapp_url():
    """Test WhatsApp URL formatting."""
    url = NotificationService.get_whatsapp_url("123456789", "Hola Mundo")
    assert "wa.me/123456789" in url
    assert "Hola%20Mundo" in url
