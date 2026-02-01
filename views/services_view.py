"""
Services view for Barber Manager.
Service management with CRUD operations.
"""
import flet as ft
from typing import Optional, List

from database import get_db
from models.base import Service
from services.service_service import ServiceService
from utils.theme import AppTheme


def create_services_view(page: ft.Page) -> ft.Control:
    """
    Create the service management view.
    Features list and CRUD operations.
    """
    services: List[dict] = []
    
    # Refs
    service_list_ref = ft.Ref[ft.Container]()
    
    def load_services():
        """Load services from database as dicts to avoid detached instance errors."""
        nonlocal services
        services = []
        with get_db() as db:
            db_services = ServiceService.get_all_services(db, active_only=False)
            for s in db_services:
                services.append({
                    "id": s.id,
                    "name": s.name,
                    "duration": s.duration,
                    "price": s.price,
                    "is_active": s.is_active
                })
    
    def refresh():
        """Refresh the view."""
        load_services()
        service_list_ref.current.content = build_service_list()
        page.update()
    
    def build_service_card(service: dict) -> ft.Control:
        """Build a single service card."""
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Icon(ft.Icons.CONTENT_CUT, color=ft.Colors.WHITE, size=24),
                        width=50, height=50,
                        bgcolor=ft.Colors.PURPLE_700 if service["is_active"] else ft.Colors.GREY_700,
                        border_radius=10, alignment=ft.Alignment(0, 0)
                    ),
                    ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(service["name"], size=16, weight=ft.FontWeight.BOLD),
                                    ft.Container(
                                        content=ft.Text(
                                            "Activo" if service["is_active"] else "Inactivo",
                                            size=10, color=ft.Colors.WHITE
                                        ),
                                        bgcolor=AppTheme.PRIMARY if service["is_active"] else ft.Colors.GREY_600,
                                        padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                        border_radius=10
                                    )
                                ],
                                spacing=10
                            ),
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.TIMER, size=14, color=ft.Colors.GREY_500),
                                    ft.Text(f"{service['duration']} minutos", size=12, color=ft.Colors.GREY_400),
                                    ft.Container(width=15),
                                    ft.Icon(ft.Icons.ATTACH_MONEY, size=14, color=ft.Colors.GREY_500),
                                    ft.Text(
                                        f"${service['price']:.2f}" if service["price"] > 0 else "Sin precio",
                                        size=12, color=ft.Colors.GREY_400
                                    )
                                ],
                                spacing=5
                            )
                        ],
                        spacing=5, expand=True
                    ),
                    ft.Row(
                        controls=[
                            ft.IconButton(icon=ft.Icons.EDIT, icon_color=AppTheme.PRIMARY, tooltip="Editar",
                                         on_click=lambda e, s=service: show_service_dialog(s)),
                            ft.IconButton(icon=ft.Icons.DELETE, icon_color=AppTheme.TEXT_ERROR, tooltip="Eliminar",
                                         on_click=lambda e, s=service: confirm_delete(s))
                        ],
                        spacing=0
                    )
                ],
                alignment=ft.MainAxisAlignment.START
            ),
            padding=15, border_radius=10, bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE)
        )
    
    def build_service_list() -> ft.Control:
        """Build the list of service cards."""
        if not services:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.CUT, size=60, color=ft.Colors.GREY_600),
                        ft.Text("No hay servicios registrados", size=16, color=ft.Colors.GREY_500)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10
                ),
                alignment=ft.Alignment(0, 0), expand=True
            )
        
        cards = [build_service_card(service) for service in services]
        return ft.ListView(controls=cards, spacing=10, expand=True)
    
    def show_service_dialog(service: Optional[dict]):
        """Show service form dialog."""
        is_edit = service is not None
        
        name_field = ft.TextField(
            label="Nombre del servicio", value=service["name"] if service else "", autofocus=True,
            border_color=AppTheme.BORDER_DEFAULT, focused_border_color=AppTheme.BORDER_FOCUS
        )
        duration_field = ft.TextField(
            label="Duración (minutos)", value=str(service["duration"]) if service else "30", keyboard_type=ft.KeyboardType.NUMBER,
            border_color=AppTheme.BORDER_DEFAULT, focused_border_color=AppTheme.BORDER_FOCUS
        )
        price_field = ft.TextField(
            label="Precio", value=str(service["price"]) if service else "0.0", keyboard_type=ft.KeyboardType.NUMBER,
            border_color=AppTheme.BORDER_DEFAULT, focused_border_color=AppTheme.BORDER_FOCUS
        )
        active_switch = ft.Switch(label="Servicio activo", value=service["is_active"] if service else True, active_color=AppTheme.PRIMARY)
        error_text = ft.Text("", color=AppTheme.TEXT_ERROR, visible=False)
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def save_service(e):
            try:
                duration = int(duration_field.value)
                price = float(price_field.value)
            except ValueError:
                error_text.value = "Duración y precio deben ser números válidos"
                error_text.visible = True
                page.update()
                return
            
            with get_db() as db:
                if is_edit:
                    result, error = ServiceService.update_service(
                        db, service_id=service["id"], name=name_field.value,
                        duration=duration, price=price, is_active=active_switch.value
                    )
                else:
                    result, error = ServiceService.create_service(
                        db, name=name_field.value, duration=duration,
                        price=price, is_active=active_switch.value
                    )
                
                if error:
                    error_text.value = error
                    error_text.visible = True
                    page.update()
                    return
            
            dialog.open = False
            refresh()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar Servicio" if is_edit else "Nuevo Servicio"),
            content=ft.Column(
                controls=[name_field, duration_field, price_field, active_switch, error_text],
                tight=True, spacing=15, width=350
            ),
            actions=[
                ft.TextButton(content=ft.Text("Cancelar"), on_click=close_dialog),
                ft.ElevatedButton(
                    content=ft.Text("Guardar", color=AppTheme.BTN_TEXT),
                    on_click=save_service,
                    style=ft.ButtonStyle(bgcolor=AppTheme.PRIMARY, color=AppTheme.BTN_TEXT)
                )
            ]
        )
        
        page.overlay.clear()
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    def confirm_delete(service: dict):
        """Show delete confirmation dialog."""
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def delete_service(e):
            with get_db() as db:
                success, error = ServiceService.delete_service(db, service["id"])
                if error:
                    page.snack_bar = ft.SnackBar(content=ft.Text(error), bgcolor=ft.Colors.RED_700)
                    page.snack_bar.open = True
            
            dialog.open = False
            refresh()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(controls=[ft.Icon(ft.Icons.WARNING, color=ft.Colors.ORANGE_400), ft.Text("Confirmar Eliminación")]),
            content=ft.Text(f"¿Estás seguro que deseas eliminar el servicio '{service['name']}'?"),
            actions=[
                ft.TextButton(content=ft.Text("Cancelar"), on_click=close_dialog),
                ft.ElevatedButton(
                    content=ft.Text("Eliminar"),
                    on_click=delete_service,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE)
                )
            ]
        )
        
        page.overlay.clear()
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    # Initial load
    load_services()
    
    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text("✂️ Servicios", size=28, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        content=ft.Text("Nuevo Servicio", color=AppTheme.BTN_TEXT),
                        icon=ft.Icons.ADD,
                        icon_color=AppTheme.BTN_TEXT,
                        on_click=lambda e: show_service_dialog(None),
                        style=ft.ButtonStyle(bgcolor=AppTheme.PRIMARY, color=AppTheme.BTN_TEXT)
                    )
                ]
            ),
            ft.Divider(height=20),
            ft.Container(
                content=build_service_list(),
                expand=True,
                bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.WHITE),
                border_radius=10, padding=15,
                ref=service_list_ref
            )
        ],
        expand=True
    )
