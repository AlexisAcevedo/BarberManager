"""
Unit tests for validators module.
"""
import pytest
from datetime import date, datetime, timedelta

from utils.validators import (
    validate_email,
    validate_phone,
    validate_name,
    validate_duration,
    validate_price,
    validate_date,
    validate_time_range,
    sanitize_string
)


class TestValidateEmail:
    """Tests for email validation."""
    
    def test_valid_email(self):
        is_valid, error = validate_email("test@example.com")
        assert is_valid is True
        assert error is None
    
    def test_valid_email_with_dots(self):
        is_valid, error = validate_email("john.doe@example.co.uk")
        assert is_valid is True
    
    def test_empty_email(self):
        is_valid, error = validate_email("")
        assert is_valid is False
        assert "requerido" in error.lower()
    
    def test_none_email(self):
        is_valid, error = validate_email(None)
        assert is_valid is False
    
    def test_invalid_email_no_at(self):
        is_valid, error = validate_email("testexample.com")
        assert is_valid is False
        assert "válido" in error.lower()
    
    def test_invalid_email_no_domain(self):
        is_valid, error = validate_email("test@")
        assert is_valid is False


class TestValidatePhone:
    """Tests for phone validation."""
    
    def test_valid_phone_digits(self):
        is_valid, error = validate_phone("1234567890")
        assert is_valid is True
        assert error is None
    
    def test_valid_phone_with_country_code(self):
        is_valid, error = validate_phone("+54 11 1234-5678")
        assert is_valid is True
    
    def test_empty_phone_is_valid(self):
        # Phone is optional
        is_valid, error = validate_phone("")
        assert is_valid is True
    
    def test_none_phone_is_valid(self):
        is_valid, error = validate_phone(None)
        assert is_valid is True
    
    def test_too_short_phone(self):
        is_valid, error = validate_phone("123")
        assert is_valid is False


class TestValidateName:
    """Tests for name validation."""
    
    def test_valid_name(self):
        is_valid, error = validate_name("John Doe")
        assert is_valid is True
        assert error is None
    
    def test_empty_name(self):
        is_valid, error = validate_name("")
        assert is_valid is False
        assert "requerido" in error.lower()
    
    def test_too_short_name(self):
        is_valid, error = validate_name("A")
        assert is_valid is False
        assert "2 caracteres" in error
    
    def test_custom_field_name(self):
        is_valid, error = validate_name("", field_name="servicio")
        assert "servicio" in error.lower()


class TestValidateDuration:
    """Tests for duration validation."""
    
    def test_valid_duration(self):
        is_valid, error = validate_duration(30)
        assert is_valid is True
        assert error is None
    
    def test_zero_duration(self):
        is_valid, error = validate_duration(0)
        assert is_valid is False
        assert "mayor a 0" in error
    
    def test_negative_duration(self):
        is_valid, error = validate_duration(-10)
        assert is_valid is False
    
    def test_excessive_duration(self):
        is_valid, error = validate_duration(1000)
        assert is_valid is False
        assert "8 horas" in error


class TestValidatePrice:
    """Tests for price validation."""
    
    def test_valid_price(self):
        is_valid, error = validate_price(25.50)
        assert is_valid is True
        assert error is None
    
    def test_zero_price_valid(self):
        is_valid, error = validate_price(0)
        assert is_valid is True
    
    def test_negative_price(self):
        is_valid, error = validate_price(-10)
        assert is_valid is False
        assert "negativo" in error
    
    def test_none_price_valid(self):
        # Price is optional
        is_valid, error = validate_price(None)
        assert is_valid is True


class TestValidateDate:
    """Tests for date validation."""
    
    def test_valid_future_date(self):
        future = date.today() + timedelta(days=7)
        is_valid, error = validate_date(future)
        assert is_valid is True
    
    def test_today_is_valid(self):
        is_valid, error = validate_date(date.today())
        assert is_valid is True
    
    def test_past_date_not_allowed(self):
        past = date.today() - timedelta(days=1)
        is_valid, error = validate_date(past, allow_past=False)
        assert is_valid is False
        assert "pasadas" in error.lower()
    
    def test_past_date_allowed(self):
        past = date.today() - timedelta(days=1)
        is_valid, error = validate_date(past, allow_past=True)
        assert is_valid is True


class TestSanitizeString:
    """Tests for string sanitization."""
    
    def test_strips_whitespace(self):
        assert sanitize_string("  hello  ") == "hello"
    
    def test_empty_string_returns_none(self):
        assert sanitize_string("   ") is None
    
    def test_none_returns_none(self):
        assert sanitize_string(None) is None
