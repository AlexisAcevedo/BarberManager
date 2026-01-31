"""
Agenda view for Barber Manager.
Main dashboard with weekly calendar and daily detail panel.
"""
import flet as ft
from datetime import datetime, date, timedelta
from typing import Optional, List

from database import get_db
from models.base import Barber
from services.appointment_service import AppointmentService
from services.notification_service import NotificationService
from services.barber_service import BarberService


def _get_week_start(d: date) -> date:
    """Get the Monday of the week containing the given date."""
    return d - timedelta(days=d.weekday())


def create_agenda_view(page: ft.Page) -> ft.Control:
    """
    Create the main agenda/dashboard view with split layout.
    Left panel (70%): Weekly view
    Right panel (30%): Daily detail
    """
    
    # State
    selected_date = date.today()
    current_week_start = _get_week_start(date.today())
    
    # Get barber_id from page.data for Flet 0.80.x
    selected_barber_id: Optional[int] = None
    if hasattr(page, 'data') and page.data is not None:
        selected_barber_id = page.data.get("barber_id")
    
    barbers: List[dict] = []
    
    # Load barbers
    with get_db() as db:
        db_barbers = db.query(Barber).filter(Barber.is_active == True).all()
        for b in db_barbers:
            barbers.append({"id": b.id, "name": b.name, "color": b.color})
            
    # selected_barber_id = None significa "todos los barberos"
    # No forzamos selección por defecto, mostramos todos
    
    # Refs for dynamic updates
    weekly_panel_ref = ft.Ref[ft.Container]()
    daily_panel_ref = ft.Ref[ft.Container]()
    week_label_ref = ft.Ref[ft.Text]()
    barber_selector_ref = ft.Ref[ft.Row]()
    
    def refresh():
        """Refresh the view."""
        nonlocal selected_date, current_week_start
        weekly_panel_ref.current.content = build_weekly_panel()
        daily_panel_ref.current.content = build_daily_panel()
        page.update()
    
    def prev_week(e):
        """Go to previous week."""
        nonlocal current_week_start
        current_week_start -= timedelta(days=7)
        refresh()
    
    def next_week(e):
        """Go to next week."""
        nonlocal current_week_start
        current_week_start += timedelta(days=7)
        refresh()
    
    def go_to_today(e):
        """Go to today."""
        nonlocal selected_date, current_week_start
        selected_date = date.today()
        current_week_start = _get_week_start(date.today())
        refresh()
    
    def select_date(d: date):
        """Select a specific date."""
        nonlocal selected_date
        selected_date = d
        refresh()

    def select_barber(barber_id):
        """Select a specific barber or None for all."""
        nonlocal selected_barber_id
        selected_barber_id = barber_id
        refresh()

    def new_appointment(e=None):
        """Navigate to new appointment screen."""
        page.go(f"/new_appointment?date={selected_date.isoformat()}&barber_id={selected_barber_id}")
    
    def new_appointment_at_time(time: datetime):
        """Navigate to new appointment with pre-selected time."""
        page.go(f"/new_appointment?date={selected_date.isoformat()}&time={time.strftime('%H:%M')}&barber_id={selected_barber_id}")
    
    def confirm_appointment(appt_id: int, client_name: str):
        """Mark an appointment as confirmed/completed."""
        with get_db() as db:
            appt, error = AppointmentService.update_appointment_status(db, appt_id, "confirmed")
            if error:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(error),
                    bgcolor=ft.Colors.RED_700
                )
            else:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"✅ Turno de {client_name} confirmado"),
                    bgcolor=ft.Colors.GREEN_700
                )
            page.snack_bar.open = True
        refresh()
    
    def send_reminder(appt_id: int):
        """Send a WhatsApp reminder."""
        with get_db() as db:
            appt = AppointmentService.get_appointment_by_id(db, appt_id)
            if appt:
                url = NotificationService.send_whatsapp_reminder(appt)
                if url:
                    page.launch_url(url)
    
    def confirm_delete_appointment(appointment_id: int, client_name: str):
        """Show confirmation dialog for deleting an appointment."""
        def close_dialog(e):
            dialog.open = False
            page.update()
        
        def delete_appointment(e):
            with get_db() as db:
                success, error = AppointmentService.delete_appointment(db, appointment_id)
                if error:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text(error),
                        bgcolor=ft.Colors.RED_700
                    )
                    page.snack_bar.open = True
                else:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Turno de {client_name} eliminado"),
                        bgcolor=ft.Colors.GREEN_700
                    )
                    page.snack_bar.open = True
            
            dialog.open = False
            refresh()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.WARNING, color=ft.Colors.ORANGE_400),
                    ft.Text("Eliminar Turno")
                ]
            ),
            content=ft.Text(f"¿Estás seguro que deseas eliminar el turno de {client_name}?"),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dialog),
                ft.ElevatedButton(
                    content=ft.Text("Eliminar"),
                    on_click=delete_appointment,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.RED_700, color=ft.Colors.WHITE)
                )
            ]
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    
    def get_week_label() -> str:
        """Get the label for the current week."""
        end_date = current_week_start + timedelta(days=6)
        months_es = [
            "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        
        if current_week_start.month == end_date.month:
            return f"{current_week_start.day} - {end_date.day} de {months_es[end_date.month]}"
        else:
            return f"{current_week_start.day} {months_es[current_week_start.month][:3]} - {end_date.day} {months_es[end_date.month][:3]}"
    
    def format_date_long(d: date) -> str:
        """Format date for display."""
        days_es = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        months_es = [
            "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        return f"{days_es[d.weekday()]}, {d.day} de {months_es[d.month]} de {d.year}"
    
    def get_appointment_count(d: date) -> int:
        """Get the number of appointments for a date and barber."""
        with get_db() as db:
            return len(AppointmentService.get_appointments_for_date(db, d, barber_id=selected_barber_id))
    
    def build_week_grid() -> ft.Control:
        """Build the 7-day week grid."""
        days_es = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        
        day_cards = []
        for i in range(7):
            day_date = current_week_start + timedelta(days=i)
            is_selected = day_date == selected_date
            is_today = day_date == date.today()
            
            appt_count = get_appointment_count(day_date)
            
            card = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            days_es[i],
                            size=12,
                            color=ft.Colors.GREY_400
                        ),
                        ft.Text(
                            str(day_date.day),
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color="#10B981" if is_today else None
                        ),
                        ft.Container(
                            content=ft.Text(
                                f"{appt_count} turnos" if appt_count != 1 else "1 turno",
                                size=10,
                                color=ft.Colors.GREY_500
                            ),
                            visible=appt_count > 0
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5
                ),
                padding=15,
                border_radius=10,
                bgcolor="#065F46" if is_selected else ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                border=ft.border.all(2, "#10B981") if is_today else None,
                on_click=lambda e, d=day_date: select_date(d),
                ink=True
            )
            day_cards.append(card)
        
        return ft.Row(
            controls=day_cards,
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            expand=True
        )
    
    def build_weekly_panel() -> ft.Control:
        """Build the weekly calendar view."""
        week_nav = ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.CHEVRON_LEFT,
                    on_click=prev_week,
                    tooltip="Semana anterior"
                ),
                ft.Text(
                    get_week_label(),
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    ref=week_label_ref
                ),
                ft.IconButton(
                    icon=ft.Icons.CHEVRON_RIGHT,
                    on_click=next_week,
                    tooltip="Semana siguiente"
                ),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    content=ft.Text("Hoy"),
                    icon=ft.Icons.TODAY,
                    on_click=go_to_today,
                    style=ft.ButtonStyle(
                        bgcolor="#10B981",
                        color=ft.Colors.WHITE
                    )
                )
            ],
            alignment=ft.MainAxisAlignment.START
        )
        
        # Chip "Todos" al inicio
        is_all_selected = selected_barber_id is None
        barber_chips = [
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.PEOPLE, size=14, color=ft.Colors.WHITE if is_all_selected else ft.Colors.GREY_400),
                    ft.Text("Todos", size=12, color=ft.Colors.WHITE if is_all_selected else ft.Colors.GREY_400)
                ], spacing=5),
                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                border_radius=20,
                bgcolor="#10B981" if is_all_selected else ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                border=ft.border.all(1, "#10B981") if is_all_selected else None,
                on_click=lambda e: select_barber(None),
            )
        ]
        
        for b in barbers:
            is_sel = b["id"] == selected_barber_id
            barber_chips.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(width=10, height=10, bgcolor=b["color"], border_radius=5),
                        ft.Text(b["name"], size=12, color=ft.Colors.WHITE if is_sel else ft.Colors.GREY_400)
                    ], spacing=5),
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                    border_radius=20,
                    bgcolor=ft.Colors.with_opacity(0.2, b["color"]) if is_sel else ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                    border=ft.border.all(1, b["color"]) if is_sel else None,
                    on_click=lambda e, bid=b["id"]: select_barber(bid),
                )
            )

        return ft.Column(
            controls=[
                ft.Row([
                    ft.Row([
                        ft.Icon(ft.Icons.CALENDAR_MONTH, color="#10B981", size=28),
                        ft.Text("Agenda Semanal", size=24, weight=ft.FontWeight.BOLD),
                    ], spacing=10),
                    ft.Container(expand=True),
                    ft.Row(controls=barber_chips, spacing=10)
                ]),
                ft.Divider(height=10),
                week_nav,
                ft.Container(height=10),
                build_week_grid()
            ],
            expand=True
        )
    
    def build_appointment_card(slot: dict) -> ft.Control:
        """Build a card for an existing appointment."""
        appt = slot["appointment"]
        client = slot["client"]
        service = slot["service"]
        
        time_str = appt["start_time"].strftime("%H:%M")
        end_str = appt["end_time"].strftime("%H:%M")
        
        status_colors = {
            "pending": ft.Colors.ORANGE_400,
            "confirmed": ft.Colors.GREEN_400,
            "cancelled": ft.Colors.RED_400
        }
        
        status_labels = {
            "pending": "Pendiente",
            "confirmed": "Confirmado",
            "cancelled": "Cancelado"
        }
        
        # Obtener color del barbero
        barber_color = slot.get("barber_color", "#2196F3")
        
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    time_str,
                                    size=16,
                                    weight=ft.FontWeight.BOLD
                                ),
                                ft.Text(
                                    end_str,
                                    size=12,
                                    color=ft.Colors.GREY_500
                                )
                            ],
                            spacing=2
                        ),
                        width=60
                    ),
                    ft.Container(
                        width=3,
                        height=50,
                        bgcolor=status_colors.get(appt["status"], ft.Colors.GREY_500),
                        border_radius=2
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                client["name"],
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                max_lines=1,
                                no_wrap=True,
                            ),
                            ft.Text(
                                service["name"],
                                size=12,
                                color=ft.Colors.GREY_400,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                max_lines=1,
                                no_wrap=True,
                            ),
                            ft.Text(
                                status_labels.get(appt["status"], appt["status"]),
                                size=10,
                                color=status_colors.get(appt["status"])
                            )
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Row(
                        controls=[
                            # Confirm button (only for pending appointments)
                            ft.IconButton(
                                icon=ft.Icons.CHECK_CIRCLE,
                                icon_color=ft.Colors.GREEN_400,
                                tooltip="Confirmar/Completar Turno",
                                on_click=lambda e, aid=appt["id"], cname=client["name"]: confirm_appointment(aid, cname),
                                visible=(appt["status"] == "pending")
                            ),
                            ft.IconButton(
                                icon=ft.Icons.NOTIFICATIONS_ACTIVE,
                                icon_color=ft.Colors.BLUE_400,
                                tooltip="Enviar Recordatorio",
                                on_click=lambda e, aid=appt["id"]: send_reminder(aid)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=ft.Colors.RED_400,
                                tooltip="Eliminar Turno",
                                on_click=lambda e, aid=appt["id"], cname=client["name"]: confirm_delete_appointment(aid, cname)
                            )
                        ],
                        spacing=0
                    )
                ],
                alignment=ft.MainAxisAlignment.START
            ),
            padding=10,
            border_radius=8,
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            border=ft.border.only(left=ft.border.BorderSide(4, barber_color))
        )
    
    def build_free_slot_card(slot: dict) -> ft.Control:
        """Build a card for a free time slot."""
        time_str = slot["time"].strftime("%H:%M")
        
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(
                            time_str,
                            size=14,
                            color=ft.Colors.GREY_500
                        ),
                        width=60
                    ),
                    ft.Container(
                        width=3,
                        height=30,
                        bgcolor=ft.Colors.GREY_700,
                        border_radius=2
                    ),
                    ft.Text(
                        "Disponible - Click para Agendar",
                        size=12,
                        color="#10B981",
                        italic=True,
                        expand=True
                    ),
                    ft.Icon(
                        ft.Icons.ADD,
                        color="#10B981",
                        size=20
                    )
                ]
            ),
            padding=10,
            border_radius=8,
            bgcolor=ft.Colors.with_opacity(0.05, "#10B981"),
            on_click=lambda e, t=slot["time"]: new_appointment_at_time(t),
            ink=True
        )
    
    def build_daily_list() -> ft.Control:
        """Build the list of appointments and free slots for selected date."""
        with get_db() as db:
            schedule = AppointmentService.get_daily_schedule(db, selected_date, barber_id=selected_barber_id)
        
        if not schedule:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            ft.Icons.EVENT_BUSY,
                            size=50,
                            color=ft.Colors.GREY_600
                        ),
                        ft.Text(
                            "No hay horarios disponibles",
                            color=ft.Colors.GREY_500
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                alignment=ft.Alignment(0, 0),
                expand=True
            )
        
        items = []
        for slot in schedule:
            if slot["type"] == "appointment":
                items.append(build_appointment_card(slot))
            else:
                items.append(build_free_slot_card(slot))
        
        return ft.ListView(
            controls=items,
            spacing=8,
            expand=True
        )
    
    def build_daily_panel() -> ft.Control:
        """Build the daily detail panel."""
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Row([
                            ft.Icon(ft.Icons.EVENT_NOTE, color="#10B981", size=24),
                            ft.Text(
                                "Detalle del Día",
                                size=20,
                                weight=ft.FontWeight.BOLD
                            ),
                        ], spacing=8
                        ),
                        ft.Container(expand=True),
                        ft.IconButton(
                            icon=ft.Icons.ADD_CIRCLE,
                            icon_color="#10B981",
                            icon_size=30,
                            tooltip="Nuevo Turno",
                            on_click=new_appointment
                        )
                    ]
                ),
                ft.Text(
                    format_date_long(selected_date),
                    size=14,
                    color=ft.Colors.GREY_400
                ),
                ft.Divider(height=15),
                ft.Container(
                    content=build_daily_list(),
                    expand=True
                )
            ],
            expand=True
        )
    
    # Build the main layout
    return ft.Row(
        controls=[
            ft.Container(
                content=build_weekly_panel(),
                expand=7,
                bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.WHITE),
                border_radius=10,
                padding=15,
                ref=weekly_panel_ref
            ),
            ft.Container(
                content=build_daily_panel(),
                expand=3,
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
                border_radius=10,
                padding=15,
                ref=daily_panel_ref
            ),
        ],
        expand=True,
        spacing=15
    )
