"""
Utilidades de validación de entrada para Barber Manager.
Proporciona validación robusta para entradas de usuario.
"""
import re
from typing import Optional, Tuple
from datetime import datetime, date


# Patrones de expresiones regulares
# Email pattern - RFC 5322 simplificado
# Previene: dominios con puntos consecutivos, guiones al inicio/fin
EMAIL_PATTERN = re.compile(
    r'^[a-zA-Z0-9][a-zA-Z0-9._%+-]*@[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$'
)

# Patrón de teléfono: permite dígitos, espacios, guiones, paréntesis y prefijo +
PHONE_PATTERN = re.compile(
    r'^\+?[\d\s\-\(\)]{7,20}$'
)


def validate_email(email: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Valida el formato de una dirección de email.
    
    Args:
        email: Dirección de email a validar
        
    Retorna:
        Tupla de (es_válido, mensaje_de_error)
    """
    if not email:
        return False, "El email es requerido"
    
    email = email.strip()
    
    if not email:
        return False, "El email no puede estar vacío"
    
    if len(email) > 150:
        return False, "El email es demasiado largo (máximo 150 caracteres)"
    
    if not EMAIL_PATTERN.match(email):
        return False, "El formato del email no es válido"
    
    return True, None


def validate_phone(phone: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Valida el formato de un número de teléfono.
    
    Args:
        phone: Número de teléfono a validar
        
    Retorna:
        Tupla de (es_válido, mensaje_de_error)
    """
    if not phone:
        return True, None  # El teléfono es opcional
    
    phone = phone.strip()
    
    if not phone:
        return True, None
    
    if len(phone) > 20:
        return False, "El teléfono es demasiado largo (máximo 20 caracteres)"
    
    if not PHONE_PATTERN.match(phone):
        return False, "El formato del teléfono no es válido"
    
    return True, None


def validate_name(name: Optional[str], field_name: str = "nombre") -> Tuple[bool, Optional[str]]:
    """
    Valida un campo de nombre.
    
    Args:
        name: Nombre a validar
        field_name: Nombre del campo para mensajes de error
        
    Retorna:
        Tupla de (es_válido, mensaje_de_error)
    """
    if not name:
        return False, f"El {field_name} es requerido"
    
    name = name.strip()
    
    if not name:
        return False, f"El {field_name} no puede estar vacío"
    
    if len(name) < 2:
        return False, f"El {field_name} debe tener al menos 2 caracteres"
    
    if len(name) > 100:
        return False, f"El {field_name} es demasiado largo (máximo 100 caracteres)"
    
    return True, None


def validate_duration(duration: Optional[int]) -> Tuple[bool, Optional[str]]:
    """
    Valida la duración de un servicio.
    
    Args:
        duration: Duración en minutos
        
    Retorna:
        Tupla de (es_válido, mensaje_de_error)
    """
    if duration is None:
        return False, "La duración es requerida"
    
    if not isinstance(duration, int):
        return False, "La duración debe ser un número entero"
    
    if duration <= 0:
        return False, "La duración debe ser mayor a 0"
    
    if duration > 480:  # Máximo 8 horas
        return False, "La duración no puede exceder 8 horas (480 minutos)"
    
    return True, None


def validate_price(price: Optional[float]) -> Tuple[bool, Optional[str]]:
    """
    Valida el precio de un servicio.
    
    Args:
        price: Valor del precio
        
    Retorna:
        Tupla de (es_válido, mensaje_de_error)
    """
    if price is None:
        return True, None  # El precio es opcional, por defecto es 0
    
    if not isinstance(price, (int, float)):
        return False, "El precio debe ser un número"
    
    if price < 0:
        return False, "El precio no puede ser negativo"
    
    if price > 1000000:
        return False, "El precio es demasiado alto"
    
    return True, None


def validate_date(
    target_date: Optional[date],
    allow_past: bool = False
) -> Tuple[bool, Optional[str]]:
    """
    Valida un valor de fecha.
    
    Args:
        target_date: Fecha a validar
        allow_past: Si se permiten fechas pasadas
        
    Retorna:
        Tupla de (es_válido, mensaje_de_error)
    """
    if not target_date:
        return False, "La fecha es requerida"
    
    if not isinstance(target_date, date):
        return False, "Formato de fecha inválido"
    
    if not allow_past and target_date < date.today():
        return False, "No se pueden agendar turnos en fechas pasadas"
    
    return True, None


def validate_time_range(
    start_time: Optional[datetime],
    end_time: Optional[datetime]
) -> Tuple[bool, Optional[str]]:
    """
    Valida un rango de tiempo.
    
    Args:
        start_time: Fecha y hora de inicio
        end_time: Fecha y hora de fin
        
    Retorna:
        Tupla de (es_válido, mensaje_de_error)
    """
    if not start_time:
        return False, "La hora de inicio es requerida"
    
    if not end_time:
        return False, "La hora de fin es requerida"
    
    if end_time <= start_time:
        return False, "La hora de fin debe ser posterior a la hora de inicio"
    
    return True, None


def sanitize_string(value: Optional[str]) -> Optional[str]:
    """
    Sanitiza un valor de cadena eliminando espacios en blanco.
    
    Args:
        value: Cadena a sanitizar
        
    Retorna:
        Cadena sanitizada o None
    """
    if not value:
        return None
    return value.strip() or None
