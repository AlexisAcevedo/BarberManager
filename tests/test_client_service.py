"""
Unit tests for ClientService.
"""
import pytest
from sqlalchemy.orm import Session

from services.client_service import ClientService
from models.base import Client


class TestClientServiceCreate:
    """Tests for ClientService.create_client"""
    
    def test_create_client_success(self, db_session: Session):
        """Test successful client creation."""
        client, error = ClientService.create_client(
            db_session,
            name="John Doe",
            email="john@example.com",
            phone="1234567890",
            notes="Regular customer"
        )
        
        assert client is not None
        assert error is None
        assert client.name == "John Doe"
        assert client.email == "john@example.com"
        assert client.phone == "1234567890"
    
    def test_create_client_without_name(self, db_session: Session):
        """Test client creation fails without name."""
        client, error = ClientService.create_client(
            db_session,
            name="",
            email="test@example.com"
        )
        
        assert client is None
        assert error == "El nombre es requerido"
    
    def test_create_client_without_email(self, db_session: Session):
        """Test client creation fails without email."""
        client, error = ClientService.create_client(
            db_session,
            name="John Doe",
            email=""
        )
        
        assert client is None
        assert error == "El email es requerido"
    
    def test_create_client_duplicate_email(self, db_session: Session, sample_client: Client):
        """Test client creation fails with duplicate email."""
        client, error = ClientService.create_client(
            db_session,
            name="Another Person",
            email=sample_client.email  # Same email
        )
        
        assert client is None
        assert "Ya existe un cliente con ese email" in error


class TestClientServiceRead:
    """Tests for ClientService read operations."""
    
    def test_get_all_clients(self, db_session: Session, sample_client: Client):
        """Test getting all clients."""
        clients = ClientService.get_all_clients(db_session)
        
        assert len(clients) >= 1
        assert any(c.id == sample_client.id for c in clients)
    
    def test_get_client_by_id(self, db_session: Session, sample_client: Client):
        """Test getting a client by ID."""
        client = ClientService.get_client_by_id(db_session, sample_client.id)
        
        assert client is not None
        assert client.id == sample_client.id
        assert client.name == sample_client.name
    
    def test_get_client_by_id_not_found(self, db_session: Session):
        """Test getting a non-existent client."""
        client = ClientService.get_client_by_id(db_session, 99999)
        
        assert client is None
    
    def test_search_clients_by_name(self, db_session: Session, sample_client: Client):
        """Test searching clients by name."""
        results = ClientService.search_clients(db_session, sample_client.name[:4])
        
        assert len(results) >= 1
        assert any(c.id == sample_client.id for c in results)
    
    def test_search_clients_empty_term(self, db_session: Session):
        """Test search with empty term returns empty list."""
        results = ClientService.search_clients(db_session, "")
        
        assert results == []


class TestClientServiceUpdate:
    """Tests for ClientService.update_client"""
    
    def test_update_client_name(self, db_session: Session, sample_client: Client):
        """Test updating client name."""
        updated, error = ClientService.update_client(
            db_session,
            client_id=sample_client.id,
            name="Updated Name"
        )
        
        assert updated is not None
        assert error is None
        assert updated.name == "Updated Name"
    
    def test_update_client_not_found(self, db_session: Session):
        """Test updating non-existent client."""
        updated, error = ClientService.update_client(
            db_session,
            client_id=99999,
            name="New Name"
        )
        
        assert updated is None
        assert error == "Cliente no encontrado"


class TestClientServiceDelete:
    """Tests for ClientService.delete_client"""
    
    def test_delete_client_success(self, db_session: Session):
        """Test deleting a client without appointments."""
        # Create a fresh client
        client, _ = ClientService.create_client(
            db_session,
            name="To Delete",
            email="delete@example.com"
        )
        db_session.commit()
        
        success, error = ClientService.delete_client(db_session, client.id)
        
        assert success is True
        assert error is None
    
    def test_delete_client_not_found(self, db_session: Session):
        """Test deleting non-existent client."""
        success, error = ClientService.delete_client(db_session, 99999)
        
        assert success is False
        assert error == "Cliente no encontrado"
