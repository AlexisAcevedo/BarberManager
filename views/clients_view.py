"""
Clients view for Barber Manager.
Client management with CRUD operations.
"""
import flet as ft
from typing import Optional, List

from database import get_db
from services.client_service import ClientService
from models.base import Client
from utils.theme import AppTheme


def create_clients_view(page: ft.Page) -> ft.Control:
    """
    Create the client management view.
    Features list, search, and CRUD operations.
    """
    clients: List[dict] = []
    
    # Refs
    client_list_ref = ft.Ref[ft.Container]()
    search_field_ref = ft.Ref[ft.TextField]()
    
    def load_clients(search_term: str = ""):
        """Load clients from database as dicts to avoid detached instance errors."""
        nonlocal clients
        clients = []
        with get_db() as db:
            if search_term:
                db_clients = ClientService.search_clients(db, search_term)
            else:
                db_clients = ClientService.get_all_clients(db)
            
            for c in db_clients:
                clients.append({
                    "id": c.id,
                    "name": c.name,
                    "email": c.email,
                    "phone": c.phone,
                    "notes": c.notes
                })
    
    def refresh():
        """Refresh the view."""
        load_clients(search_field_ref.current.value if search_field_ref.current else "")
        client_list_ref.current.content = build_client_list()
        page.update()
    
    def on_search(e: ft.ControlEvent):
        """Handle search input."""
        load_clients(e.control.value)
        client_list_ref.current.content = build_client_list()
        page.update()
    
    def build_client_card(client: dict) -> ft.Control:
        """Build a single client card."""
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(
                            client["name"][0].upper() if client["name"] else "?",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE
                        ),
                        width=50,
                        height=50,

                        bgcolor=AppTheme.PRIMARY,
                        border_radius=25,
                        alignment=ft.Alignment(0, 0)
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(client["name"], size=16, weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY),
                            ft.Text(client["email"], size=12, color=AppTheme.TEXT_SECONDARY),
                            ft.Text(client["phone"] or "Sin teléfono", size=12, color=AppTheme.TEXT_SECONDARY)
                        ],
                        spacing=2,
                        expand=True
                    ),
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_color=AppTheme.PRIMARY,
                                tooltip="Editar",
                                on_click=lambda e, c=client: show_client_dialog(c)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=AppTheme.TEXT_ERROR,
                                tooltip="Eliminar",
                                on_click=lambda e, c=client: confirm_delete(c)
                            )
                        ],
                        spacing=0
                    )
                ],
                alignment=ft.MainAxisAlignment.START
            ),
            padding=15,
            border_radius=10,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE)
        )
    
    def build_client_list() -> ft.Control:
        """Build the list of client cards."""
        if not clients:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.PEOPLE_OUTLINE, size=60, color=ft.Colors.GREY_600),
                        ft.Text("No hay clientes registrados", size=16, color=ft.Colors.GREY_500),
                        ft.Text("Haz clic en 'Nuevo Cliente' para agregar uno", size=12, color=ft.Colors.GREY_600)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10
                ),
                alignment=ft.Alignment(0, 0),
                expand=True
            )
        
        cards = [build_client_card(client) for client in clients]
        return ft.ListView(controls=cards, spacing=10, expand=True)
    
    def show_client_dialog(client: Optional[dict]):
        """Show client form dialog."""
        is_edit = client is not None
        
        name_field = ft.TextField(
            label="Nombre", value=client["name"] if client else "", autofocus=True,
            border_color=AppTheme.BORDER_DEFAULT, focused_border_color=AppTheme.BORDER_FOCUS
        )
        email_field = ft.TextField(
            label="Email", value=client["email"] if client else "",
            border_color=AppTheme.BORDER_DEFAULT, focused_border_color=AppTheme.BORDER_FOCUS
        )
        phone_field = ft.TextField(
            label="Teléfono", value=client["phone"] if client else "",
            border_color=AppTheme.BORDER_DEFAULT, focused_border_color=AppTheme.BORDER_FOCUS
        )
        notes_field = ft.TextField(
            label="Notas", value=client["notes"] if client else "", multiline=True, min_lines=2, max_lines=4,
            border_color=AppTheme.BORDER_DEFAULT, focused_border_color=AppTheme.BORDER_FOCUS
        )
        error_text = ft.Text("", color=AppTheme.TEXT_ERROR, visible=False)
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def save_client(e):
            with get_db() as db:
                if is_edit:
                    result, error = ClientService.update_client(
                        db, client_id=client["id"], name=name_field.value,
                        email=email_field.value, phone=phone_field.value, notes=notes_field.value
                    )
                else:
                    result, error = ClientService.create_client(
                        db, name=name_field.value, email=email_field.value,
                        phone=phone_field.value, notes=notes_field.value
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
            title=ft.Text("Editar Cliente" if is_edit else "Nuevo Cliente"),
            content=ft.Column(
                controls=[name_field, email_field, phone_field, notes_field, error_text],
                tight=True, spacing=15, width=400
            ),
            actions=[
                ft.TextButton(content=ft.Text("Cancelar"), on_click=close_dialog),
                ft.ElevatedButton(
                    content=ft.Text("Guardar", color=AppTheme.BTN_TEXT), 
                    on_click=save_client, 
                    style=ft.ButtonStyle(bgcolor=AppTheme.PRIMARY)
                )
            ]
        )
        
        page.overlay.clear()
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    def confirm_delete(client: dict):
        """Show delete confirmation dialog."""
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def delete_client(e):
            with get_db() as db:
                success, error = ClientService.delete_client(db, client["id"])
                if error:
                    page.snack_bar = ft.SnackBar(content=ft.Text(error), bgcolor=ft.Colors.RED_700)
                    page.snack_bar.open = True
            
            dialog.open = False
            refresh()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(controls=[ft.Icon(ft.Icons.WARNING, color=ft.Colors.ORANGE_400), ft.Text("Confirmar Eliminación")]),
            content=ft.Text(f"¿Estás seguro que deseas eliminar a {client['name']}?"),
            actions=[
                ft.TextButton(content=ft.Text("Cancelar"), on_click=close_dialog),
                ft.ElevatedButton(
                    content=ft.Text("Eliminar"),
                    on_click=delete_client,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE)
                )
            ]
        )
        
        page.overlay.clear()
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    # Initial load
    load_clients()
    
    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text("👥 Clientes", size=28, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.ElevatedButton(
                        content=ft.Text("Nuevo Cliente", color=AppTheme.BTN_TEXT),
                        icon=ft.Icons.PERSON_ADD,
                        icon_color=AppTheme.BTN_TEXT,
                        on_click=lambda e: show_client_dialog(None),
                        style=ft.ButtonStyle(bgcolor=AppTheme.PRIMARY, color=AppTheme.BTN_TEXT)
                    )
                ]
            ),
            ft.Divider(height=20),
            ft.Row(controls=[
                ft.TextField(
                    label="Buscar clientes...", prefix_icon=ft.Icons.SEARCH,
                    on_change=on_search, border_radius=10, expand=True, ref=search_field_ref,
                    border_color=AppTheme.BORDER_DEFAULT, focused_border_color=AppTheme.BORDER_FOCUS
                )
            ]),
            ft.Container(height=15),
            ft.Container(
                content=build_client_list(),
                expand=True,
                bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.WHITE),
                border_radius=10, padding=15,
                ref=client_list_ref
            )
        ],
        expand=True
    )
