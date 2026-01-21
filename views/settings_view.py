"""
Settings view for Barber Manager.
Configuration and preferences.
"""
import flet as ft

from database import get_db, reset_db
from services.settings_service import SettingsService


def create_settings_view(page: ft.Page) -> ft.Control:
    """
    Create the settings/configuration view.
    Allows editing of business hours and other preferences.
    """
    
    # Load current settings
    start_hour = 12
    end_hour = 20
    with get_db() as db:
        start_hour, end_hour = SettingsService.get_business_hours(db)
    
    # Refs for dropdowns
    start_dropdown_ref = ft.Ref[ft.Dropdown]()
    end_dropdown_ref = ft.Ref[ft.Dropdown]()
    
    def build_section(title: str, subtitle: str, controls: list) -> ft.Control:
        """Build a settings section."""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(title, size=18, weight=ft.FontWeight.W_500),
                    ft.Text(subtitle, size=12, color=ft.Colors.GREY_500),
                    ft.Container(height=10),
                    *controls
                ]
            ),
            padding=20,
            border_radius=10,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE)
        )
    
    def save_business_hours(e):
        """Save business hours to database."""
        try:
            if not start_dropdown_ref.current or not end_dropdown_ref.current:
                show_error("Error: No se pudieron obtener los valores")
                return
            
            start = int(start_dropdown_ref.current.value.split(":")[0])
            end = int(end_dropdown_ref.current.value.split(":")[0])
            
            if end <= start:
                show_error("La hora de cierre debe ser mayor a la de apertura")
                return
            
            with get_db() as db:
                SettingsService.set_business_hours(db, start, end)
            
            # Show success dialog
            def close_success(e):
                success_dialog.open = False
                page.update()
            
            success_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_400, size=30),
                        ft.Text("¡Horario Guardado!")
                    ],
                    spacing=10
                ),
                content=ft.Text(
                    f"El horario de atención se ha actualizado:\n"
                    f"Apertura: {start:02d}:00\n"
                    f"Cierre: {end:02d}:00"
                ),
                actions=[
                    ft.ElevatedButton(
                        content=ft.Text("Aceptar"),
                        on_click=close_success,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)
                    )
                ]
            )
            
            page.overlay.clear()
            page.overlay.append(success_dialog)
            success_dialog.open = True
            page.update()
            
        except Exception as ex:
            show_error(f"Error: {ex}")
    
    def show_error(message: str):
        """Show error message."""
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED_700
        )
        page.snack_bar.open = True
        page.update()
    
    def confirm_reset_db(e):
        """Show confirmation dialog for database reset."""
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def do_reset(e):
            reset_db()
            dialog.open = False
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Base de datos reiniciada correctamente"),
                bgcolor=ft.Colors.GREEN_700
            )
            page.snack_bar.open = True
            page.push_route("/")
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(controls=[ft.Icon(ft.Icons.WARNING, color=ft.Colors.RED_400), ft.Text("¡Advertencia!")]),
            content=ft.Text(
                "Esta acción eliminará TODOS los datos (clientes, turnos, etc.) "
                "y reiniciará la base de datos con los servicios por defecto.\n\n"
                "¿Estás completamente seguro?"
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dialog),
                ft.ElevatedButton(
                    content=ft.Text("Sí, reiniciar"),
                    on_click=do_reset,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE)
                )
            ]
        )
        
        page.overlay.clear()
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    return ft.Column(
        controls=[
            ft.Text("⚙️ Configuración", size=28, weight=ft.FontWeight.BOLD),
            ft.Divider(height=20),
            
            build_section(
                "Horario de Trabajo", "Configura el horario de atención",
                [
                    ft.Row(controls=[
                        ft.Text("Hora de apertura:", width=150),
                        ft.Dropdown(
                            ref=start_dropdown_ref,
                            value=f"{start_hour:02d}:00",
                            options=[ft.dropdown.Option(f"{h:02d}:00") for h in range(6, 16)],
                            width=120
                        )
                    ]),
                    ft.Row(controls=[
                        ft.Text("Hora de cierre:", width=150),
                        ft.Dropdown(
                            ref=end_dropdown_ref,
                            value=f"{end_hour:02d}:00",
                            options=[ft.dropdown.Option(f"{h:02d}:00") for h in range(14, 24)],
                            width=120
                        )
                    ]),
                    ft.Container(height=10),
                    ft.ElevatedButton(
                        content=ft.Text("Guardar Horario"),
                        icon=ft.Icons.SAVE,
                        on_click=save_business_hours,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)
                    )
                ]
            ),
            ft.Container(height=20),
            
            build_section(
                "Google Calendar", "Sincronización con Google Calendar",
                [
                    ft.Row(controls=[ft.Icon(ft.Icons.CLOUD_OFF, color=ft.Colors.ORANGE_400), ft.Text("No conectado", color=ft.Colors.ORANGE_400)], spacing=10),
                    ft.ElevatedButton(
                        content=ft.Text("Conectar Google Calendar"),
                        icon=ft.Icons.LINK,
                        disabled=True,
                        tooltip="Próximamente"
                    ),
                    ft.Text("La integración con Google Calendar estará disponible próximamente", size=12, color=ft.Colors.GREY_500, italic=True)
                ]
            ),
            ft.Container(height=20),
            
            build_section(
                "Base de Datos", "Gestión de datos",
                [
                    ft.ElevatedButton(
                        content=ft.Text("Reiniciar Base de Datos"),
                        icon=ft.Icons.REFRESH,
                        on_click=confirm_reset_db,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE)
                    ),
                    ft.Text("⚠️ Esta acción eliminará todos los datos", size=12, color=ft.Colors.RED_400)
                ]
            ),
            ft.Container(height=20),
            
            build_section(
                "Acerca de", "Información de la aplicación",
                [
                    ft.Text("Barber Manager v1.0.0", size=14),
                    ft.Text("Aplicación de gestión para barberías", size=12, color=ft.Colors.GREY_500),
                    ft.Text("Desarrollado con Flet + SQLAlchemy", size=12, color=ft.Colors.GREY_500)
                ]
            )
        ],
        expand=True,
        scroll=ft.ScrollMode.AUTO
    )
