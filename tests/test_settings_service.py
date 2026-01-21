"""
Unit tests for SettingsService.
"""
import pytest
from services.settings_service import SettingsService
from models.base import Settings

def test_get_setting_default(db_session):
    """Test getting a setting that doesn't exist returns default."""
    value = SettingsService.get_setting(db_session, "business_hours_start")
    assert value == "12"

def test_set_and_get_setting(db_session):
    """Test setting and then getting a configuration value."""
    SettingsService.set_setting(db_session, "test_key", "test_value")
    db_session.commit()
    
    value = SettingsService.get_setting(db_session, "test_key")
    assert value == "test_value"

def test_update_setting(db_session):
    """Test updating an existing setting."""
    SettingsService.set_setting(db_session, "theme", "light")
    db_session.commit()
    
    SettingsService.set_setting(db_session, "theme", "dark")
    db_session.commit()
    
    value = SettingsService.get_setting(db_session, "theme")
    assert value == "dark"

def test_set_get_business_hours(db_session):
    """Test setting and getting business hours."""
    SettingsService.set_business_hours(db_session, 8, 18)
    db_session.commit()
    
    start, end = SettingsService.get_business_hours(db_session)
    assert start == 8
    assert end == 18
