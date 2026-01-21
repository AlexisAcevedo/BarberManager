"""
Servicio de notificaciones para Barber Manager.
Maneja recordatorios por WhatsApp y Email.
"""
import urllib.parse
from typing import Optional
from models.base import Appointment, Client, Service


class NotificationService:
    """
    Capa de servicio para envío de notificaciones a clientes.
    """

    @staticmethod
    def get_whatsapp_url(phone: str, message: str) -> str:
        """
        Genera una URL de WhatsApp para click-to-chat.
        
        Args:
            phone: Número de teléfono del destinatario
            message: Mensaje a enviar
            
        Retorna:
            URL de WhatsApp formateada
        """
        if not phone:
            return ""
        clean_phone = ''.join(filter(str.isdigit, phone))
        encoded_msg = urllib.parse.quote(message)
        return f"https://wa.me/{clean_phone}?text={encoded_msg}"

    @classmethod
    def generate_reminder_message(cls, appointment: Appointment) -> str:
        """
        Genera un mensaje de recordatorio estándar.
        
        Args:
            appointment: Turno para el cual generar el recordatorio
            
        Retorna:
            Mensaje formateado con los detalles del turno
        """
        start_time = appointment.start_time.strftime("%H:%M")
        date_str = appointment.start_time.strftime("%d/%m")
        return (
            f"Hola {appointment.client.name}! Te recordamos tu turno en "
            f"Barbería Pro para el día {date_str} a las {start_time} "
            f"({appointment.service.name}). ¡Te esperamos!"
        )

    @classmethod
    def send_whatsapp_reminder(cls, appointment: Appointment) -> str:
        """
        Retorna la URL para enviar un recordatorio manual por WhatsApp.
        
        Args:
            appointment: Turno para el cual enviar el recordatorio
            
        Retorna:
            URL de WhatsApp con el mensaje pre-cargado
        """
        msg = cls.generate_reminder_message(appointment)
        return cls.get_whatsapp_url(appointment.client.phone, msg)
