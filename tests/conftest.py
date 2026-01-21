"""
Pytest configuration and fixtures for Barber Manager tests.
"""
import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from models.base import Base, Client, Service, Appointment, Barber, User


# Test database - in-memory SQLite
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_engine():
    """Create a fresh database engine for each test."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """Create a database session for testing."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def sample_client(db_session: Session) -> Client:
    """Create a sample client for testing."""
    client = Client(
        name="Test Client",
        email="test@example.com",
        phone="1234567890",
        notes="Test notes"
    )
    db_session.add(client)
    db_session.commit()
    return client


@pytest.fixture
def sample_service(db_session: Session) -> Service:
    """Create a sample service for testing."""
    service = Service(
        name="Test Service",
        duration=30,
        price=50.0,
        is_active=True
    )
    db_session.add(service)
    db_session.commit()
    return service


@pytest.fixture
def sample_services(db_session: Session) -> list:
    """Create multiple sample services for testing."""
    services = [
        Service(name="Corte", duration=30, price=25.0, is_active=True),
        Service(name="Barba", duration=15, price=15.0, is_active=True),
        Service(name="Combo", duration=45, price=35.0, is_active=True),
        Service(name="Inactive Service", duration=60, price=100.0, is_active=False),
    ]
    for service in services:
        db_session.add(service)
    db_session.commit()
    return services
@pytest.fixture
def sample_barber(db_session: Session) -> Barber:
    """Create a sample barber for testing."""
    barber = Barber(name="Test Barber", color="#FF5722")
    db_session.add(barber)
    db_session.commit()
    return barber

@pytest.fixture
def sample_user(db_session: Session, sample_barber: Barber) -> User:
    """Create a sample user for testing."""
    from services.auth_service import AuthService
    user, _ = AuthService.create_user(
        db_session, 
        username="testuser", 
        password="testpassword",
        barber_id=sample_barber.id
    )
    db_session.commit()
    return user
