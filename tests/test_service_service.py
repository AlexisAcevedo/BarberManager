"""
Unit tests for ServiceService.
"""
import pytest
from sqlalchemy.orm import Session

from services.service_service import ServiceService
from models.base import Service


class TestServiceServiceCreate:
    """Tests for ServiceService.create_service"""
    
    def test_create_service_success(self, db_session: Session):
        """Test successful service creation."""
        service, error = ServiceService.create_service(
            db_session,
            name="New Service",
            duration=45,
            price=35.0,
            is_active=True
        )
        
        assert service is not None
        assert error is None
        assert service.name == "New Service"
        assert service.duration == 45
        assert service.price == 35.0
    
    def test_create_service_without_name(self, db_session: Session):
        """Test service creation fails without name."""
        service, error = ServiceService.create_service(
            db_session,
            name="",
            duration=30
        )
        
        assert service is None
        assert error == "El nombre es requerido"
    
    def test_create_service_invalid_duration(self, db_session: Session):
        """Test service creation fails with zero duration."""
        service, error = ServiceService.create_service(
            db_session,
            name="Test Service",
            duration=0
        )
        
        assert service is None
        assert error == "La duración debe ser mayor a 0"
    
    def test_create_service_negative_duration(self, db_session: Session):
        """Test service creation fails with negative duration."""
        service, error = ServiceService.create_service(
            db_session,
            name="Test Service",
            duration=-10
        )
        
        assert service is None
        assert error == "La duración debe ser mayor a 0"
    
    def test_create_service_duplicate_name(self, db_session: Session, sample_service: Service):
        """Test service creation fails with duplicate name."""
        service, error = ServiceService.create_service(
            db_session,
            name=sample_service.name,
            duration=60
        )
        
        assert service is None
        assert "Ya existe un servicio con ese nombre" in error


class TestServiceServiceRead:
    """Tests for ServiceService read operations."""
    
    def test_get_all_services_active_only(self, db_session: Session, sample_services: list):
        """Test getting only active services."""
        services = ServiceService.get_all_services(db_session, active_only=True)
        
        assert len(services) == 3  # Excludes inactive
        assert all(s.is_active for s in services)
    
    def test_get_all_services_include_inactive(self, db_session: Session, sample_services: list):
        """Test getting all services including inactive."""
        services = ServiceService.get_all_services(db_session, active_only=False)
        
        assert len(services) == 4  # Includes inactive
    
    def test_get_service_by_id(self, db_session: Session, sample_service: Service):
        """Test getting a service by ID."""
        service = ServiceService.get_service_by_id(db_session, sample_service.id)
        
        assert service is not None
        assert service.id == sample_service.id
    
    def test_get_service_by_id_not_found(self, db_session: Session):
        """Test getting a non-existent service."""
        service = ServiceService.get_service_by_id(db_session, 99999)
        
        assert service is None


class TestServiceServiceUpdate:
    """Tests for ServiceService.update_service"""
    
    def test_update_service_name(self, db_session: Session, sample_service: Service):
        """Test updating service name."""
        updated, error = ServiceService.update_service(
            db_session,
            service_id=sample_service.id,
            name="Updated Service Name"
        )
        
        assert updated is not None
        assert error is None
        assert updated.name == "Updated Service Name"
    
    def test_update_service_duration(self, db_session: Session, sample_service: Service):
        """Test updating service duration."""
        updated, error = ServiceService.update_service(
            db_session,
            service_id=sample_service.id,
            duration=60
        )
        
        assert updated is not None
        assert updated.duration == 60
    
    def test_update_service_invalid_duration(self, db_session: Session, sample_service: Service):
        """Test updating with invalid duration fails."""
        updated, error = ServiceService.update_service(
            db_session,
            service_id=sample_service.id,
            duration=0
        )
        
        assert updated is None
        assert error == "La duración debe ser mayor a 0"
    
    def test_update_service_not_found(self, db_session: Session):
        """Test updating non-existent service."""
        updated, error = ServiceService.update_service(
            db_session,
            service_id=99999,
            name="New Name"
        )
        
        assert updated is None
        assert error == "Servicio no encontrado"


class TestServiceServiceDelete:
    """Tests for ServiceService.delete_service"""
    
    def test_delete_service_success(self, db_session: Session):
        """Test deleting a service without appointments."""
        # Create a fresh service
        service, _ = ServiceService.create_service(
            db_session,
            name="To Delete",
            duration=30
        )
        db_session.commit()
        
        success, error = ServiceService.delete_service(db_session, service.id)
        
        assert success is True
        assert error is None
    
    def test_delete_service_not_found(self, db_session: Session):
        """Test deleting non-existent service."""
        success, error = ServiceService.delete_service(db_session, 99999)
        
        assert success is False
        assert error == "Servicio no encontrado"
