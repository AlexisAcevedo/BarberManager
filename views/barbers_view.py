"""
Vista de gestión de barberos para Barber Manager.
Permite crear, editar y desactivar barberos.
"""
import flet as ft
from database import get_db
from services.barber_service import BarberService


def create_barbers_view(page: ft.Page) -> ft.Control:
    """
    Crea la vista de gestión de barberos.
    """
    # Estado local
    barbers_list = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    
    def load_barbers():
        """Carga la lista de barberos desde la base de datos."""
        try:
            with get_db() as db:
                barbers = BarberService.get_all_barbers(db, include_inactive=True)
                
                barbers_list.controls.clear()
                
                if not barbers:
                    barbers_list.controls.append(
                        ft.Container(
                            content=ft.Text(
                                "No hay barberos registrados",
                                size=16,
                                color=ft.Colors.GREY_500
                            ),
                            padding=20
                        )
                    )
                else:
                    for barber in barbers:
                        card = create_barber_card(barber, db)
                        barbers_list.controls.append(card)
                        
                page.update()
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error cargando barberos: {e}")
    
    def create_barber_card(barber, db) -> ft.Container:
        """Crea una tarjeta visual para un barbero."""
        stats = BarberService.get_barber_stats(db, barber.id)
        
        # Badge de estado
        status_controls = [
            ft.Text(
                barber.name,
                size=18,
                weight=ft.FontWeight.BOLD
            )
        ]
        
        if not barber.is_active:
            status_controls.append(
                ft.Container(
                    content=ft.Text(
                        "INACTIVO",
                        size=10,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE
                    ),
                    bgcolor=ft.Colors.RED_700,
                    padding=5,
                    border_radius=5
                )
            )
        
        return ft.Container(
            content=ft.Row(
                controls=[
                    # Indicador de color
                    ft.Container(
                        width=6,
                        height=70,
                        bgcolor=barber.color,
                        border_radius=3
                    ),
                    # Información del barbero
                    ft.Column(
                        controls=[
                            ft.Row(controls=status_controls, spacing=10),
                            ft.Text(
                                f"📅 {stats['total_appointments']} citas | "
                                f"✅ {stats['completed']} | ❌ {stats['cancelled']}",
                                size=12,
                                color=ft.Colors.GREY_600
                            ),
                        ],
                        spacing=5,
                        expand=True
                    ),
                    # Botones de acción
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                tooltip="Editar",
                                on_click=lambda e, b=barber: show_edit_dialog(b)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.POWER_SETTINGS_NEW,
                                tooltip="Desactivar" if barber.is_active else "Activar",
                                icon_color=ft.Colors.RED_700 if barber.is_active else ft.Colors.GREEN_700,
                                on_click=lambda e, b=barber: toggle_barber_status(b)
                            ),
                        ],
                        spacing=0
                    )
                ],
                spacing=10
            ),
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
            border_radius=8,
            padding=10
        )
    
    def show_create_dialog():
        """Muestra el diálogo para crear un nuevo barbero."""
        name_field = ft.TextField(
            label="Nombre del barbero",
            hint_text="Ej: Juan Pérez",
            autofocus=True
        )
        
        color_field = ft.TextField(
            label="Color (formato #RRGGBB)",
            value="#2196F3"
        )
        
        error_text = ft.Text(color=ft.Colors.RED_700, visible=False)
        
        def close_dialog():
            dialog.open = False
            page.update()
        
        def do_create(e):
            with get_db() as db:
                barber, error = BarberService.create_barber(
                    db,
                    name=name_field.value,
                    color=color_field.value
                )
                
                if error:
                    error_text.value = error
                    error_text.visible = True
                    page.update()
                else:
                    db.commit()
                    close_dialog()
                    load_barbers()
                    show_snackbar(f"Barbero '{barber.name}' creado", ft.Colors.GREEN_700)
        
        dialog = ft.AlertDialog(
            title=ft.Text("➕ Nuevo Barbero"),
            content=ft.Column([name_field, color_field, error_text], tight=True, width=350),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: close_dialog()),
                ft.ElevatedButton("Crear", on_click=do_create)
            ]
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    def show_edit_dialog(barber):
        """Muestra el diálogo para editar un barbero."""
        name_field = ft.TextField(label="Nombre", value=barber.name)
        color_field = ft.TextField(label="Color", value=barber.color)
        error_text = ft.Text(color=ft.Colors.RED_700, visible=False)
        
        def close_dialog():
            dialog.open = False
            page.update()
        
        def do_update(e):
            with get_db() as db:
                updated, error = BarberService.update_barber(
                    db, barber.id, name_field.value, color_field.value
                )
                if error:
                    error_text.value = error
                    error_text.visible = True
                    page.update()
                else:
                    db.commit()
                    close_dialog()
                    load_barbers()
                    show_snackbar("Barbero actualizado", ft.Colors.GREEN_700)
        
        dialog = ft.AlertDialog(
            title=ft.Text(f"✏️ Editar: {barber.name}"),
            content=ft.Column([name_field, color_field, error_text], tight=True, width=350),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: close_dialog()),
                ft.ElevatedButton("Guardar", on_click=do_update)
            ]
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    def toggle_barber_status(barber):
        """Activa o desactiva un barbero."""
        action = "desactivar" if barber.is_active else "activar"
        
        def close_dialog():
            dialog.open = False
            page.update()
        
        def do_toggle(e):
            with get_db() as db:
                updated, error = BarberService.toggle_active(db, barber.id)
                if error:
                    close_dialog()
                    show_snackbar(error, ft.Colors.RED_700)
                else:
                    db.commit()
                    close_dialog()
                    load_barbers()
                    show_snackbar(f"Barbero {action}do", ft.Colors.GREEN_700)
        
        dialog = ft.AlertDialog(
            title=ft.Text(f"⚠️ {action.capitalize()}"),
            content=ft.Text(f"¿{action.capitalize()} a '{barber.name}'?"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: close_dialog()),
                ft.ElevatedButton(action.capitalize(), on_click=do_toggle)
            ]
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    def show_snackbar(message, color):
        """Muestra un snackbar con mensaje."""
        page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=color)
        page.snack_bar.open = True
        page.update()
    
    # Retornar el contenido (load_barbers se llama después)
    content = ft.Column(
        controls=[
            ft.Row([
                ft.Text("👨‍💼 Gestión de Barberos", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.IconButton(icon=ft.Icons.REFRESH, tooltip="Actualizar", on_click=lambda e: load_barbers())
            ]),
            ft.Divider(height=10),
            ft.ElevatedButton("➕ Nuevo Barbero", icon=ft.Icons.ADD, on_click=lambda e: show_create_dialog()),
            ft.Container(height=10),
            barbers_list
        ],
        expand=True,
        spacing=10
    )
    
    # Cargar datos iniciales
    load_barbers()
    
    return content
