"""
Appointment Card Component.
A reusable card to display appointment details with action buttons.
"""
import flet as ft
from typing import Callable, Optional, Dict, Any


def create_appointment_card(
    appointment: Dict[str, Any],
    on_delete: Optional[Callable[[int, str], None]] = None,
    on_chat: Optional[Callable[[str], None]] = None,
) -> ft.Container:
    """
    Create an appointment card component.
    
    Args:
        appointment: Dictionary with appointment data including nested client and service
        on_delete: Callback function(appointment_id, client_name) for delete action
        on_chat: Callback function(phone) for WhatsApp action
        
    Returns:
        ft.Container: The styled appointment card
    """
    client = appointment.get("client", {})
    service = appointment.get("service", {})
    
    client_name = client.get("name", "Cliente desconocido")
    client_phone = client.get("phone", "")
    service_name = service.get("name", "Servicio")
    start_time = appointment.get("start_time")
    end_time = appointment.get("end_time")
    status = appointment.get("status", "pending")
    appointment_id = appointment.get("id")
    
    # Format time
    time_str = ""
    if start_time and end_time:
        time_str = f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
    
    # Status styling
    status_colors = {
        "pending": ft.Colors.ORANGE_400,
        "confirmed": ft.Colors.GREEN_400,
        "completed": ft.Colors.BLUE_400,
        "cancelled": ft.Colors.RED_400,
    }
    status_labels = {
        "pending": "Pendiente",
        "confirmed": "Confirmado",
        "completed": "Completado",
        "cancelled": "Cancelado",
    }
    
    # Action buttons
    action_buttons = []
    
    if client_phone and on_chat:
        action_buttons.append(
            ft.IconButton(
                icon=ft.Icons.CHAT,
                icon_color=ft.Colors.GREEN_400,
                tooltip="Enviar WhatsApp",
                on_click=lambda e: on_chat(client_phone)
            )
        )
    
    if on_delete:
        action_buttons.append(
            ft.IconButton(
                icon=ft.Icons.DELETE,
                icon_color=ft.Colors.RED_400,
                tooltip="Eliminar Turno",
                on_click=lambda e: on_delete(appointment_id, client_name)
            )
        )
    
    return ft.Container(
        content=ft.Row(
            controls=[
                # Left side - Time and info
                ft.Column(
                    controls=[
                        ft.Text(time_str, size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(client_name, size=14),
                        ft.Text(service_name, size=12, color=ft.Colors.GREY_400),
                    ],
                    spacing=2,
                    expand=True,
                ),
                # Right side - Status and actions
                ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Text(
                                status_labels.get(status, status),
                                size=10,
                                color=ft.Colors.WHITE,
                            ),
                            bgcolor=status_colors.get(status, ft.Colors.GREY_600),
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            border_radius=4,
                        ),
                        ft.Row(
                            controls=action_buttons,
                            spacing=0,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.END,
                    spacing=5,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=10,
        border_radius=8,
        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
    )
