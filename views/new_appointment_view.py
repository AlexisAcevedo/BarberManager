"""
New Appointment view for Barber Manager.
Form with smart time slot selection and conflict detection.
"""
import flet as ft
from datetime import datetime, date, timedelta
from typing import Optional, List
from urllib.parse import parse_qs

from database import get_db
from services.appointment_service import AppointmentService
from services.client_service import ClientService
from services.service_service import ServiceService
from models.base import Client, Service, Barber


def create_new_appointment_view(page: ft.Page, query_params: Optional[str] = None) -> ft.Control:
    """
    Create the new appointment form.
    Features:
    - Client search with autocomplete
    - Service selection
    - Smart time chips with conflict detection
    """
    # Parse query parameters
    initial_date = date.today()
    initial_time: Optional[str] = None
    selected_barber_id: Optional[int] = None
    
    if query_params:
        params = parse_qs(query_params)
        if "date" in params:
            try:
                initial_date = date.fromisoformat(params["date"][0])
            except ValueError:
                pass
        if "time" in params:
            initial_time = params["time"][0]
        if "barber_id" in params:
            try:
                selected_barber_id = int(params["barber_id"][0])
            except ValueError:
                pass
    
    # State
    selected_client: Optional[dict] = None
    selected_service: Optional[dict] = None
    selected_time: Optional[str] = None
    available_slots: List[tuple] = []
    barbers: List[dict] = []

    # Load barbers
    with get_db() as db:
        db_barbers = db.query(Barber).filter(Barber.is_active == True).all()
        for b in db_barbers:
            barbers.append({"id": b.id, "name": b.name, "color": b.color})
    
    if not selected_barber_id and barbers:
        selected_barber_id = barbers[0]["id"]
    
    # Load services - convert to dicts to avoid detached instance errors
    services = []
    with get_db() as db:
        db_services = ServiceService.get_all_services(db)
        for s in db_services:
            services.append({
                "id": s.id,
                "name": s.name,
                "duration": s.duration,
                "price": s.price,
                "is_active": s.is_active
            })
    
    # Refs for dynamic updates
    client_field_ref = ft.Ref[ft.TextField]()
    client_results_ref = ft.Ref[ft.Column]()
    selected_client_card_ref = ft.Ref[ft.Container]()
    service_chips_row_ref = ft.Ref[ft.Row]()
    time_chips_container_ref = ft.Ref[ft.Column]()
    confirm_btn_ref = ft.Ref[ft.ElevatedButton]()
    barber_selector_ref = ft.Ref[ft.Row]()
    
    def format_date(d: date) -> str:
        """Format date for display."""
        days_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        months_es = [
            "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        return f"{days_es[d.weekday()]}, {d.day} de {months_es[d.month]} de {d.year}"
    
    def update_confirm_button():
        """Update confirm button state."""
        can_confirm = (
            selected_client is not None and
            selected_service is not None and
            selected_time is not None and
            selected_barber_id is not None
        )
        confirm_btn_ref.current.disabled = not can_confirm
        page.update()
    
    def on_client_search(e: ft.ControlEvent):
        """Handle client search input."""
        search_term = e.control.value
        
        if len(search_term) < 2:
            client_results_ref.current.controls.clear()
            page.update()
            return
        
        # Convert to dicts inside session to avoid detached instance errors
        client_dicts = []
        with get_db() as db:
            clients = ClientService.search_clients(db, search_term)
            for c in clients:
                client_dicts.append({
                    "id": c.id,
                    "name": c.name,
                    "email": c.email,
                    "phone": c.phone
                })
        
        client_results_ref.current.controls.clear()
        
        for client in client_dicts:
            result_item = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.PERSON_OUTLINE, size=20),
                        ft.Column(
                            controls=[
                                ft.Text(client["name"], size=14),
                                ft.Text(
                                    client["phone"] or client["email"],
                                    size=12,
                                    color=ft.Colors.GREY_500
                                )
                            ],
                            spacing=0,
                            expand=True
                        )
                    ]
                ),
                padding=10,
                border_radius=8,
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                on_click=lambda e, c=client: select_client(c),
                ink=True
            )
            client_results_ref.current.controls.append(result_item)
        
        if not client_dicts:
            client_results_ref.current.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No se encontraron clientes",
                        color=ft.Colors.GREY_500,
                        italic=True
                    ),
                    padding=10
                )
            )
        
        page.update()
    
    def select_client(client: dict):
        """Select a client."""
        nonlocal selected_client
        selected_client = client
        
        # Hide search results and show selected card
        client_results_ref.current.controls.clear()
        client_field_ref.current.value = ""
        client_field_ref.current.visible = False
        
        selected_client_card_ref.current.content = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(ft.Icons.PERSON, color=ft.Colors.GREEN_400),
                    padding=10,
                    bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.GREEN),
                    border_radius=25
                ),
                ft.Column(
                    controls=[
                        ft.Text(client["name"], size=16, weight=ft.FontWeight.BOLD),
                        ft.Text(client["email"], size=12, color=ft.Colors.GREY_400),
                        ft.Text(client["phone"] or "", size=12, color=ft.Colors.GREY_500)
                    ],
                    spacing=2,
                    expand=True
                ),
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    icon_color=ft.Colors.RED_400,
                    tooltip="Cambiar cliente",
                    on_click=clear_client
                )
            ]
        )
        selected_client_card_ref.current.padding = 10
        selected_client_card_ref.current.border_radius = 8
        selected_client_card_ref.current.bgcolor = ft.Colors.with_opacity(0.1, ft.Colors.GREEN)
        selected_client_card_ref.current.visible = True
        
        update_confirm_button()
    
    def select_barber(barber_id: int):
        """Update selected barber and refresh slots."""
        nonlocal selected_barber_id
        selected_barber_id = barber_id
        update_time_slots()
        update_confirm_button()

    def clear_client(e):
        """Clear selected client."""
        nonlocal selected_client
        selected_client = None
        selected_client_card_ref.current.visible = False
        client_field_ref.current.visible = True
        update_confirm_button()
    
    def select_service(service_id: int):
        """Select a service by ID and update time slots."""
        nonlocal selected_service
        
        # Find the service by ID
        selected_service = next((s for s in services if s["id"] == service_id), None)
        if not selected_service:
            return
        
        # Update chip styles
        for chip in service_chips_row_ref.current.controls:
            if chip.data == service_id:
                chip.bgcolor = ft.Colors.BLUE_900
                chip.border = ft.border.all(2, ft.Colors.BLUE_400)
            else:
                chip.bgcolor = ft.Colors.with_opacity(0.1, ft.Colors.WHITE)
                chip.border = ft.border.all(1, ft.Colors.GREY_700)
        
        update_time_slots()
        update_confirm_button()
    
    def update_time_slots():
        """Update time slots based on selected service."""
        nonlocal available_slots
        
        if not selected_service:
            return
        
        with get_db() as db:
            available_slots = AppointmentService.get_available_slots(
                db, 
                initial_date, 
                selected_service["duration"],
                barber_id=selected_barber_id
            )
        
        # Build time chips grouped by hour
        time_rows = []
        current_hour = None
        current_row_chips = []
        
        for hour, minute, is_available in available_slots:
            if current_hour != hour:
                if current_row_chips:
                    time_rows.append(
                        ft.Row(
                            controls=current_row_chips,
                            wrap=True,
                            spacing=8
                        )
                    )
                current_row_chips = []
                current_hour = hour
            
            time_str = f"{hour:02d}:{minute:02d}"
            is_selected = selected_time == time_str
            
            chip = ft.Container(
                content=ft.Text(
                    time_str,
                    size=14,
                    color=ft.Colors.WHITE if (is_available and not is_selected) else 
                          (ft.Colors.WHITE if is_selected else ft.Colors.GREY_600)
                ),
                padding=ft.padding.symmetric(horizontal=15, vertical=8),
                border_radius=8,
                bgcolor=(
                    ft.Colors.GREEN_700 if is_selected else
                    ft.Colors.BLUE_800 if is_available else
                    ft.Colors.with_opacity(0.1, ft.Colors.WHITE)
                ),
                on_click=(
                    (lambda e, t=time_str: select_time(t)) if is_available else None
                ),
                ink=is_available,
                tooltip=(
                    "Seleccionar" if is_available else 
                    "No disponible - conflicto con otro turno"
                ),
                data={"time": time_str, "available": is_available}  # Store data for style updates
            )
            current_row_chips.append(chip)
        
        # Add last row
        if current_row_chips:
            time_rows.append(
                ft.Row(
                    controls=current_row_chips,
                    wrap=True,
                    spacing=8
                )
            )
        
        # Count available slots
        available_count = sum(1 for _, _, avail in available_slots if avail)
        
        time_chips_container_ref.current.controls = [
            ft.Text(
                f"Servicio: {selected_service['name']} ({selected_service['duration']} min) • "
                f"{available_count} horarios disponibles",
                size=12,
                color=ft.Colors.GREY_400
            ),
            ft.Divider(height=10),
            *time_rows
        ]
        
        page.update()
        
        # Note: Pre-selection of initial_time is handled at service selection level
        # Do NOT call select_time() from here to avoid recursion
    
    def select_time(time_str: str):
        """Select a time slot."""
        nonlocal selected_time
        selected_time = time_str
        
        # Update styling visually without rebuilding controls (avoids recursion)
        if time_chips_container_ref.current:
            for control in time_chips_container_ref.current.controls:
                if isinstance(control, ft.Row):
                    for chip in control.controls:
                        if isinstance(chip, ft.Container) and chip.data:
                            is_match = chip.data.get("time") == time_str
                            is_avail = chip.data.get("available")
                            
                            chip.bgcolor = (
                                ft.Colors.GREEN_700 if is_match else
                                ft.Colors.BLUE_800 if is_avail else
                                ft.Colors.with_opacity(0.1, ft.Colors.WHITE)
                            )
                            # Text color is white for both selected and available states
        
        update_confirm_button()
        page.update()
    
    def confirm_appointment(e):
        """Confirm and create the appointment."""
        if not all([selected_client, selected_service, selected_time]):
            return
        
        # Parse time
        hour, minute = map(int, selected_time.split(":"))
        start_time = datetime.combine(
            initial_date,
            datetime.min.time().replace(hour=hour, minute=minute)
        )
        
        # Create appointment
        with get_db() as db:
            appointment, error = AppointmentService.create_appointment(
                db,
                client_id=selected_client["id"],
                service_id=selected_service["id"],
                barber_id=selected_barber_id,
                start_time=start_time,
                sync_to_google=True
            )
            
            if error:
                show_error_dialog(error)
                return
        
        show_success_dialog()
    
    def show_new_client_dialog(e):
        """Show dialog to create a new client."""
        name_field = ft.TextField(label="Nombre", autofocus=True)
        email_field = ft.TextField(label="Email")
        phone_field = ft.TextField(label="Teléfono")
        error_text = ft.Text("", color=ft.Colors.RED_400, visible=False)
        
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def save_client(e):
            with get_db() as db:
                client, error = ClientService.create_client(
                    db,
                    name=name_field.value,
                    email=email_field.value,
                    phone=phone_field.value
                )
                
                if error:
                    error_text.value = error
                    error_text.visible = True
                    page.update()
                    return
                
                # Convert to dict before session closes
                client_dict = {
                    "id": client.id,
                    "name": client.name,
                    "email": client.email,
                    "phone": client.phone
                }
            
            # Call select_client outside the session with serialized data
            select_client(client_dict)
            dialog.open = False
            page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nuevo Cliente"),
            content=ft.Column(
                controls=[name_field, email_field, phone_field, error_text],
                tight=True,
                spacing=15
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dialog),
                ft.ElevatedButton(
                    content=ft.Text("Guardar"),
                    on_click=save_client,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)
                )
            ]
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    def show_error_dialog(message: str):
        """Show error dialog."""
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.ERROR, color=ft.Colors.RED_400),
                    ft.Text("Error")
                ]
            ),
            content=ft.Text(message),
            actions=[
                ft.TextButton("Cerrar", on_click=close_dialog)
            ]
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    def show_success_dialog():
        """Show success dialog."""
        def go_to_agenda(e):
            dialog.open = False
            page.go("/")
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_400),
                    ft.Text("¡Turno Creado!")
                ]
            ),
            content=ft.Text(
                f"El turno para {selected_client['name']} ha sido agendado "
                f"para las {selected_time}."
            ),
            actions=[
                ft.ElevatedButton(
                    content=ft.Text("Volver a la Agenda"),
                    on_click=go_to_agenda,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE)
                )
            ]
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    # Build service chips
    service_chips = []
    for service in services:
        chip = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        service["name"],
                        size=14,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Text(
                        f"{service['duration']} min",
                        size=12,
                        color=ft.Colors.GREY_400
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=10),
            border_radius=10,
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            border=ft.border.all(1, ft.Colors.GREY_700),
            on_click=lambda e, sid=service["id"]: select_service(sid),
            ink=True,
            data=service["id"]
        )
        service_chips.append(chip)
    
    # Build the form
    return ft.Container(
        content=ft.Column(
            controls=[
                # Header
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            on_click=lambda e: page.go("/"),
                            tooltip="Volver"
                        ),
                        ft.Text(
                            "📅 Nuevo Turno",
                            size=28,
                            weight=ft.FontWeight.BOLD
                        ),
                    ]
                ),
                ft.Text(
                    format_date(initial_date),
                    size=14,
                    color=ft.Colors.GREY_400
                ),
                ft.Divider(height=20),
                
                # Step 1: Client search
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.PERSON, color=ft.Colors.BLUE_400),
                                    ft.Text(
                                        "Paso 1: Seleccionar Cliente",
                                        size=18,
                                        weight=ft.FontWeight.W_500
                                    ),
                                    ft.Container(expand=True),
                                    ft.TextButton(
                                        "+ Nuevo Cliente",
                                        on_click=show_new_client_dialog
                                    )
                                ]
                            ),
                            ft.Container(visible=False, ref=selected_client_card_ref),
                            ft.TextField(
                                label="Buscar Cliente (Nombre o Teléfono)",
                                prefix_icon=ft.Icons.SEARCH,
                                hint_text="Escribe para buscar...",
                                on_change=on_client_search,
                                border_radius=10,
                                ref=client_field_ref
                            ),
                            ft.Column(controls=[], spacing=5, ref=client_results_ref)
                        ]
                    ),
                    padding=15,
                    border_radius=10,
                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE)
                ),
                ft.Container(height=20),
                
                # Step 2: Service selection
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.CUT, color=ft.Colors.BLUE_400),
                                    ft.Text(
                                        "Paso 2: Seleccionar Servicio",
                                        size=18,
                                        weight=ft.FontWeight.W_500
                                    )
                                ]
                            ),
                            ft.Container(height=10),
                            ft.Row(
                                controls=service_chips,
                                wrap=True,
                                spacing=10,
                                ref=service_chips_row_ref
                            ),
                            ft.Divider(height=20),
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.PERSON_PIN, color=ft.Colors.BLUE_400),
                                    ft.Text("Barbero:", weight=ft.FontWeight.W_500),
                                    ft.Row(
                                        controls=[
                                            ft.Container(
                                                content=ft.Text(b["name"], size=12),
                                                padding=ft.padding.symmetric(horizontal=12, vertical=5),
                                                bgcolor=b["color"] if b["id"] == selected_barber_id else ft.Colors.with_opacity(0.1, b["color"]),
                                                border_radius=5,
                                                on_click=lambda e, bid=b["id"]: select_barber(bid)
                                            ) for b in barbers
                                        ],
                                        spacing=5
                                    )
                                ]
                            )
                        ]
                    ),
                    padding=15,
                    border_radius=10,
                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE)
                ),
                ft.Container(height=20),
                
                # Step 3: Time selection
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.ACCESS_TIME, color=ft.Colors.BLUE_400),
                                    ft.Text(
                                        "Paso 3: Seleccionar Horario",
                                        size=18,
                                        weight=ft.FontWeight.W_500
                                    ),
                                    ft.Container(expand=True),
                                    ft.Text(
                                        "Horario: 12:00 - 20:00",
                                        size=12,
                                        color=ft.Colors.GREY_500
                                    )
                                ]
                            ),
                            ft.Container(height=10),
                            ft.Column(
                                controls=[
                                    ft.Container(
                                        content=ft.Text(
                                            "Selecciona un servicio primero",
                                            color=ft.Colors.GREY_500,
                                            italic=True
                                        ),
                                        alignment=ft.Alignment(0, 0),
                                        padding=20
                                    )
                                ],
                                ref=time_chips_container_ref
                            )
                        ]
                    ),
                    padding=15,
                    border_radius=10,
                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE)
                ),
                ft.Container(height=30),
                
                # Confirm button
                ft.Container(
                    content=ft.ElevatedButton(
                        content=ft.Text("Confirmar y Sincronizar"),
                        icon=ft.Icons.CHECK_CIRCLE,
                        width=300,
                        height=50,
                        disabled=True,
                        style=ft.ButtonStyle(
                            bgcolor=ft.Colors.GREEN_700,
                            color=ft.Colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=10)
                        ),
                        on_click=confirm_appointment,
                        ref=confirm_btn_ref
                    ),
                    alignment=ft.Alignment(0, 0)
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True
        ),
        padding=20,
        expand=True
    )
