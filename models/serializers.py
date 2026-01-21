"""
Model serializers for Barber Manager.
Provides functions to convert ORM objects to dictionaries,
avoiding SQLAlchemy detached instance errors.
"""
from typing import Dict, Any, List, Optional
from models.base import Client, Service, Appointment


def serialize_client(client: Client) -> Dict[str, Any]:
    """
    Serialize a Client ORM object to a dictionary.
    
    Args:
        client: Client ORM object
        
    Returns:
        Dictionary representation of the client
    """
    return {
        "id": client.id,
        "name": client.name,
        "email": client.email,
        "phone": client.phone,
        "notes": client.notes,
        "created_at": client.created_at
    }


def serialize_clients(clients: List[Client]) -> List[Dict[str, Any]]:
    """
    Serialize a list of Client objects.
    
    Args:
        clients: List of Client ORM objects
        
    Returns:
        List of client dictionaries
    """
    return [serialize_client(c) for c in clients]


def serialize_service(service: Service) -> Dict[str, Any]:
    """
    Serialize a Service ORM object to a dictionary.
    
    Args:
        service: Service ORM object
        
    Returns:
        Dictionary representation of the service
    """
    return {
        "id": service.id,
        "name": service.name,
        "duration": service.duration,
        "price": service.price,
        "is_active": service.is_active
    }


def serialize_services(services: List[Service]) -> List[Dict[str, Any]]:
    """
    Serialize a list of Service objects.
    
    Args:
        services: List of Service ORM objects
        
    Returns:
        List of service dictionaries
    """
    return [serialize_service(s) for s in services]


def serialize_appointment(appointment: Appointment) -> Dict[str, Any]:
    """
    Serialize an Appointment ORM object to a dictionary.
    Includes nested client and service data.
    
    Args:
        appointment: Appointment ORM object
        
    Returns:
        Dictionary representation of the appointment
    """
    return {
        "id": appointment.id,
        "client_id": appointment.client_id,
        "service_id": appointment.service_id,
        "start_time": appointment.start_time,
        "end_time": appointment.end_time,
        "status": appointment.status,
        "google_event_id": appointment.google_event_id,
        "created_at": appointment.created_at,
        "client": serialize_client(appointment.client) if appointment.client else None,
        "service": serialize_service(appointment.service) if appointment.service else None
    }


def serialize_appointment_minimal(appointment: Appointment) -> Dict[str, Any]:
    """
    Serialize an Appointment with minimal data (no nested objects).
    
    Args:
        appointment: Appointment ORM object
        
    Returns:
        Dictionary representation without nested objects
    """
    return {
        "id": appointment.id,
        "start_time": appointment.start_time,
        "end_time": appointment.end_time,
        "status": appointment.status
    }


def serialize_appointments(appointments: List[Appointment]) -> List[Dict[str, Any]]:
    """
    Serialize a list of Appointment objects.
    
    Args:
        appointments: List of Appointment ORM objects
        
    Returns:
        List of appointment dictionaries
    """
    return [serialize_appointment(a) for a in appointments]
