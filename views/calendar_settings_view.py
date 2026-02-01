"""
Vista de configuración de Google Calendar.
Permite conectar con Google Calendar y gestionar la sincronización.
"""
import flet as ft
import threading
from typing import Optional

from database import get_db
from services.google_calendar_service import GoogleCalendarService
from services.settings_service import SettingsService

class CalendarSettingsView(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.main_page = page # type: ignore
        self.google_service = GoogleCalendarService()
        self.is_connecting = False
        
        # UI References
        self.status_icon = ft.Ref[ft.Icon]()
        self.status_text = ft.Ref[ft.Text]()
        self.connect_btn = ft.Ref[ft.ElevatedButton]()
        self.enable_switch = ft.Ref[ft.Switch]()
        self.manual_sync_btn = ft.Ref[ft.ElevatedButton]()
        self.calendar_dropdown = ft.Ref[ft.Dropdown]()
        self.loading_ring = ft.Ref[ft.ProgressRing]()

        # Container config
        self.padding = 30
        self.expand = True
        self.content = self._build_ui()

    def did_mount(self):
        # Bind event handlers manually
        if self.calendar_dropdown.current:
            self.calendar_dropdown.current.on_change = self.change_calendar
        self.check_status()
        
    def check_status(self):
        """Check connection status and update UI."""
        is_auth = self.google_service.is_authenticated()
        
        if is_auth:
            self.status_icon.current.name = ft.Icons.CHECK_CIRCLE
            self.status_icon.current.color = ft.Colors.GREEN
            self.status_text.current.value = "Conectado a Google Calendar"
            self.status_text.current.color = ft.Colors.GREEN
            self.connect_btn.current.text = "Re-conectar"
            self.connect_btn.current.visible = True
            
            # Enable controls
            self.enable_switch.current.disabled = False
            self.manual_sync_btn.current.disabled = False
            self.calendar_dropdown.current.disabled = False
            
            # Load settings
            with get_db() as db:
                enabled = SettingsService.is_google_calendar_enabled(db)
                self.enable_switch.current.value = enabled
                
                # Load calendars if we are connected
                if enabled or True: # Always load calendars if connected
                    self.load_calendars(db)
        else:
            self.status_icon.current.name = ft.Icons.ERROR_OUTLINE
            self.status_icon.current.color = ft.Colors.GREY
            self.status_text.current.value = "No conectado"
            self.status_text.current.color = ft.Colors.GREY
            self.connect_btn.current.text = "Conectar con Google Calendar"
            
            # Disable controls
            self.enable_switch.current.disabled = True
            self.enable_switch.current.value = False
            self.manual_sync_btn.current.disabled = True
            self.calendar_dropdown.current.disabled = True
            
        self.loading_ring.current.visible = False
        self.update()

    def load_calendars(self, db):
        """Load available calendars into dropdown."""
        calendars = self.google_service.get_calendars()
        current_cal_id = SettingsService.get_google_calendar_id(db)
        
        options = []
        found_current = False
        
        for cal in calendars:
            options.append(ft.dropdown.Option(
                key=cal['id'],
                text=cal['summary'] + (" (Principal)" if cal.get('primary') else "")
            ))
            if cal['id'] == current_cal_id:
                found_current = True
                
        self.calendar_dropdown.current.options = options
        
        # If no calendars found or error
        if not options:
            options.append(ft.dropdown.Option("primary", "Principal"))
            
        # Select current
        if found_current:
            self.calendar_dropdown.current.value = current_cal_id
        else:
            self.calendar_dropdown.current.value = "primary" # Default
            
        self.update()

    def connect_click(self, e):
        """Handle connect button click."""
        self.is_connecting = True
        self.connect_btn.current.disabled = True
        self.loading_ring.current.visible = True
        self.status_text.current.value = "Iniciando autenticación en navegador..."
        self.update()
        
        # Run auth in separate thread to not block UI
        threading.Thread(target=self._run_auth_flow, daemon=True).start()
        
    def _run_auth_flow(self):
        """Run the actual auth flow."""
        success = self.google_service.authenticate()
        self.is_connecting = False
        
        # Schedule UI update on main thread
        # In Flet we can just call update() from thread usually, but safer to just update
        # check_status handles UI update
        self.check_status() 
        
        if not success:
            error = self.google_service.get_last_error()
            self.main_page.snack_bar = ft.SnackBar(ft.Text(f"Error: {error}"), bgcolor=ft.Colors.RED)
            self.main_page.snack_bar.open = True
            self.main_page.update()
        else:
             self.main_page.snack_bar = ft.SnackBar(ft.Text("¡Conectado exitosamente!"), bgcolor=ft.Colors.GREEN)
             self.main_page.snack_bar.open = True
             self.main_page.update()

    def toggle_sync(self, e):
        """Toggle sync enable/disable."""
        with get_db() as db:
            SettingsService.set_google_calendar_enabled(db, self.enable_switch.current.value)
            
        if self.enable_switch.current.value:
            # If enabling, maybe refresh calendars
            with get_db() as db:
                self.load_calendars(db)

    def change_calendar(self, e):
        """Handle calendar selection change."""
        if not self.calendar_dropdown.current.value:
            return
            
        with get_db() as db:
            SettingsService.set_google_calendar_id(db, self.calendar_dropdown.current.value)

    def manual_sync_click(self, e):
        """Trigger manual sync."""
        self.main_page.snack_bar = ft.SnackBar(ft.Text("Sincronización manual iniciada... (Implementación pendiente)"), bgcolor=ft.Colors.BLUE)
        self.main_page.snack_bar.open = True
        self.main_page.update()
        # TODO: Implement bulk sync in AppointmentService

    def _build_ui(self):
        return ft.Column(
            controls=[
                ft.Text("Configuración de Google Calendar", size=24, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                
                # Status Section
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ERROR_OUTLINE, color=ft.Colors.GREY, ref=self.status_icon, size=40),
                        ft.Column([
                            ft.Text("Estado de Conexión", weight=ft.FontWeight.BOLD),
                            ft.Text("No conectado", ref=self.status_text, color=ft.Colors.GREY),
                        ]),
                        ft.Container(expand=True),
                        ft.ProgressRing(ref=self.loading_ring, visible=False, width=20, height=20),
                        ft.ElevatedButton(
                            "Conectar con Google Calendar", 
                            icon=ft.Icons.LOGIN,
                            on_click=self.connect_click,
                            ref=self.connect_btn
                        )
                    ]),
                    padding=20,
                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                    border_radius=10,
                    border=ft.border.all(1, ft.Colors.GREY_300)
                ),
                
                ft.Divider(height=30),
                
                # Settings Section
                ft.Text("Opciones de Sincronización", size=18, weight=ft.FontWeight.BOLD),
                
                ft.Container(
                    content=ft.Column([
                        ft.Switch(
                            label="Habilitar sincronización automática",
                            value=False,
                            on_change=self.toggle_sync,
                            ref=self.enable_switch,
                            disabled=True
                        ),
                        ft.Container(height=10),
                        ft.Text("Calendario Destino:"),
                        ft.Dropdown(
                            options=[],
                            ref=self.calendar_dropdown,
                            disabled=True,
                            width=400
                        ),
                    ]),
                    padding=20
                ),
                
                ft.Divider(height=30),
                
                # Actions Section
                ft.Text("Acciones", size=18, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.ElevatedButton(
                        "Sincronizar Todo Ahora",
                        icon=ft.Icons.SYNC,
                        on_click=self.manual_sync_click,
                        ref=self.manual_sync_btn,
                        disabled=True
                    ),
                    # ft.OutlinedButton("Desconectar", icon=ft.Icons.LOGOUT, color=ft.Colors.RED) # TODO
                ])
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )

def create_calendar_settings_view(page: ft.Page):
    return CalendarSettingsView(page)
