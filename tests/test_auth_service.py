"""
Unit tests for AuthService.
"""
import pytest
from services.auth_service import AuthService
from models.base import Barber, User

def test_create_user(db_session, sample_barber):
    """Test user creation with hashed password."""
    user, error = AuthService.create_user(
        db_session, 
        username="newuser", 
        password="securepass",
        barber_id=sample_barber.id
    )
    assert error is None
    assert user.username == "newuser"
    assert user.password_hash != "securepass"  # Must be hashed

def test_authenticate_success(db_session, sample_user):
    """Test successful authentication."""
    user = AuthService.authenticate(db_session, "testuser", "testpassword")
    assert user is not None
    assert user.id == sample_user.id

def test_authenticate_fail_wrong_password(db_session, sample_user):
    """Test failed authentication due to wrong password."""
    user = AuthService.authenticate(db_session, "testuser", "wrongpass")
    assert user is None

def test_authenticate_fail_nonexistent_user(db_session):
    """Test failed authentication for non-existent user."""
    user = AuthService.authenticate(db_session, "ghost", "anypass")
    assert user is None
