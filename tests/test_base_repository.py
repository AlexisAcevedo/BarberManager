"""
Tests para el repositorio base genérico.
"""
import pytest
from models.base import Client, Service
from repositories.base_repository import BaseRepository


class TestBaseRepository:
    """Tests para BaseRepository."""
    
    def test_create(self, db_session):
        """Test crear un registro."""
        repo = BaseRepository(Client)
        client = Client(
            name="Test Client",
            email="test@example.com",
            phone="123456789"
        )
        created = repo.create(db_session, client)
        
        assert created.id is not None
        assert created.name == "Test Client"
    
    def test_get_by_id(self, db_session):
        """Test obtener registro por ID."""
        repo = BaseRepository(Client)
        client = Client(
            name="Get Test",
            email="get@example.com"
        )
        repo.create(db_session, client)
        db_session.commit()
        
        found = repo.get_by_id(db_session, client.id)
        assert found is not None
        assert found.name == "Get Test"
    
    def test_get_by_id_not_found(self, db_session):
        """Test obtener registro inexistente."""
        repo = BaseRepository(Client)
        found = repo.get_by_id(db_session, 99999)
        assert found is None
    
    def test_get_all(self, db_session):
        """Test obtener todos los registros."""
        repo = BaseRepository(Service)
        
        # Crear algunos servicios
        s1 = Service(name="Servicio A", duration=30)
        s2 = Service(name="Servicio B", duration=45)
        repo.create(db_session, s1)
        repo.create(db_session, s2)
        db_session.commit()
        
        all_services = repo.get_all(db_session)
        assert len(all_services) >= 2
    
    def test_delete(self, db_session):
        """Test eliminar registro."""
        repo = BaseRepository(Client)
        client = Client(
            name="Delete Test",
            email="delete@example.com"
        )
        repo.create(db_session, client)
        db_session.commit()
        client_id = client.id
        
        result = repo.delete(db_session, client_id)
        db_session.commit()
        
        assert result is True
        assert repo.get_by_id(db_session, client_id) is None
    
    def test_delete_not_found(self, db_session):
        """Test eliminar registro inexistente."""
        repo = BaseRepository(Client)
        result = repo.delete(db_session, 99999)
        assert result is False
