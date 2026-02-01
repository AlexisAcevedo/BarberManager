"""
Reports view for Barber Manager.
Dashboard with daily cash register (arqueo de caja) and period analytics.
"""
import flet as ft
from datetime import date, datetime, timedelta
from database import get_db
from repositories.appointment_repository import AppointmentRepository
from utils.theme import AppTheme

appointment_repo = AppointmentRepository()

def create_reports_view(page: ft.Page) -> ft.Control:
    """
    Create the reports/analytics dashboard with daily and period views.
    Shows confirmed (caja), pending, and cancelled appointments separately.
    """
    # State
    selected_date = date.today()
    view_mode = "daily"  # "daily" or "period"
    period_start = date.today().replace(day=1)
    period_end = date.today()
    
    # References for UI updates
    content_container = ft.Ref[ft.Column]()
    date_display = ft.Ref[ft.Text]()
    mode_switch = ft.Ref[ft.Switch]()
    period_row = ft.Ref[ft.Row]()
    period_start_text = ft.Ref[ft.Text]()
    period_end_text = ft.Ref[ft.Text]()
    
    def get_stats(start: date, end: date):
        """Fetch statistics grouped by status for the given date range."""
        with get_db() as db:
            stats = appointment_repo.get_stats_by_status(db, start, end)
            barber_stats = appointment_repo.get_barber_performance(db, start, end, status="confirmed")
        return stats, barber_stats

    def create_stat_card(title: str, value: str, subtitle: str, icon: str, color: str):
        """Create a statistics card with income subtitle."""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(icon, color=color, size=28),
                    ft.Text(title, size=13, color=AppTheme.TEXT_SECONDARY),
                    ft.Text(value, size=26, weight=ft.FontWeight.BOLD),
                    ft.Text(subtitle, size=12, color=color),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4
            ),
            bgcolor=ft.Colors.with_opacity(0.08, color),
            padding=15,
            border_radius=12,
            expand=True
        )

    def build_stats_content(start: date, end: date, is_daily: bool):
        """Build the statistics content for display."""
        stats, barber_stats = get_stats(start, end)
        
        # Period label
        if is_daily:
            period_label = f"📅 Arqueo de Caja - {start.strftime('%A %d/%m/%Y').capitalize()}"
        else:
            period_label = f"📊 Reporte: {start.strftime('%d/%m/%Y')} al {end.strftime('%d/%m/%Y')}"
        
        # Status cards row
        status_cards = ft.Row(
            controls=[
                create_stat_card(
                    "💰 Caja (Confirmados)", 
                    str(stats["confirmed"]["count"]),
                    f"${stats['confirmed']['income']:.2f}",
                    ft.Icons.CHECK_CIRCLE, 
                    AppTheme.PRIMARY
                ),
                create_stat_card(
                    "⏳ Pendientes", 
                    str(stats["pending"]["count"]),
                    f"${stats['pending']['income']:.2f} esperado",
                    ft.Icons.SCHEDULE, 
                    ft.Colors.ORANGE_400
                ),
                create_stat_card(
                    "❌ Cancelados", 
                    str(stats["cancelled"]["count"]),
                    "Sin recaudación",
                    ft.Icons.CANCEL, 
                    AppTheme.TEXT_ERROR
                ),
            ],
            spacing=15
        )
        
        # Total summary
        total_row = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.SUMMARIZE, color=ft.Colors.BLUE_400, size=24),
                    ft.Text("Total del día:", size=16, weight=ft.FontWeight.W_500),
                    ft.Text(
                        f"{stats['total']['count']} turnos", 
                        size=16,
                        color=AppTheme.TEXT_SECONDARY
                    ),
                    ft.Container(expand=True),
                    ft.Text(
                        f"Recaudación real: ${stats['confirmed']['income']:.2f}",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=AppTheme.PRIMARY
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLUE_400),
            padding=15,
            border_radius=10,
        )
        
        # Barber performance table (only confirmed appointments)
        if barber_stats:
            barber_rows = [
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(b["name"])),
                        ft.DataCell(ft.Text(str(b["count"]))),
                        ft.DataCell(ft.Text(f"${b['income']:.2f}")),
                    ]
                ) for b in barber_stats
            ]
        else:
            barber_rows = [
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("Sin turnos confirmados", color=AppTheme.TEXT_SECONDARY)),
                        ft.DataCell(ft.Text("-")),
                        ft.DataCell(ft.Text("-")),
                    ]
                )
            ]
        
        barber_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Barbero")),
                ft.DataColumn(ft.Text("Turnos Atendidos"), numeric=True),
                ft.DataColumn(ft.Text("Recaudación"), numeric=True),
            ],
            rows=barber_rows,
            expand=True
        )
        
        return [
            ft.Text(period_label, size=20, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            status_cards,
            ft.Container(height=15),
            total_row,
            ft.Container(height=25),
            ft.Text("💈 Desempeño por Barbero (solo confirmados)", size=16, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=barber_table,
                bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.WHITE),
                padding=10,
                border_radius=10
            )
        ]

    def refresh_content():
        """Refresh the displayed statistics based on current mode and dates."""
        nonlocal view_mode, selected_date, period_start, period_end
        
        if view_mode == "daily":
            start = end = selected_date
        else:
            start = period_start
            end = period_end
        
        # Update content
        content_container.current.controls = build_stats_content(start, end, view_mode == "daily")
        page.update()

    def on_date_change(e):
        """Handle single date picker change."""
        nonlocal selected_date
        if e.control.value:
            selected_date = e.control.value.date() if isinstance(e.control.value, datetime) else e.control.value
            date_display.current.value = selected_date.strftime("%d/%m/%Y")
            refresh_content()

    def on_period_start_change(e):
        """Handle period start date change."""
        nonlocal period_start
        if e.control.value:
            period_start = e.control.value.date() if isinstance(e.control.value, datetime) else e.control.value
            period_start_text.current.value = period_start.strftime("%d/%m/%Y")
            refresh_content()

    def on_period_end_change(e):
        """Handle period end date change."""
        nonlocal period_end
        if e.control.value:
            period_end = e.control.value.date() if isinstance(e.control.value, datetime) else e.control.value
            period_end_text.current.value = period_end.strftime("%d/%m/%Y")
            refresh_content()

    def on_mode_switch(e):
        """Toggle between daily and period view."""
        nonlocal view_mode
        view_mode = "period" if e.control.value else "daily"
        period_row.current.visible = (view_mode == "period")
        refresh_content()

    def open_date_picker(e):
        """Open the date picker dialog."""
        date_picker.open = True
        page.update()

    def open_period_start_picker(e):
        """Open the period start date picker."""
        period_start_picker.open = True
        page.update()

    def open_period_end_picker(e):
        """Open the period end date picker."""
        period_end_picker.open = True
        page.update()

    # Date pickers
    date_picker = ft.DatePicker(
        first_date=date(2020, 1, 1),
        last_date=date.today(),
        on_change=on_date_change,
    )
    
    period_start_picker = ft.DatePicker(
        first_date=date(2020, 1, 1),
        last_date=date.today(),
        on_change=on_period_start_change,
    )
    
    period_end_picker = ft.DatePicker(
        first_date=date(2020, 1, 1),
        last_date=date.today(),
        on_change=on_period_end_change,
    )
    
    # Add pickers to page overlay
    page.overlay.extend([date_picker, period_start_picker, period_end_picker])
    
    # Header with date selector
    header_row = ft.Row(
        controls=[

            ft.Text("📊 Reportes", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            ft.Text("Ver periodo:", size=13, color=AppTheme.TEXT_SECONDARY),
            ft.Switch(
                ref=mode_switch,
                value=False,
                on_change=on_mode_switch,
                active_color=AppTheme.PRIMARY,
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
    
    # Daily date selector
    daily_date_row = ft.Row(
        controls=[
            ft.Icon(ft.Icons.CALENDAR_TODAY, color=AppTheme.PRIMARY, size=20),
            ft.Text("Fecha:", color=AppTheme.TEXT_SECONDARY),
            ft.TextButton(
                content=ft.Text(
                    ref=date_display,
                    value=selected_date.strftime("%d/%m/%Y"),
                    size=15,
                ),
                on_click=open_date_picker,
            ),
        ],
        spacing=8,
    )
    
    # Period date selectors (hidden by default)
    period_selector_row = ft.Row(
        ref=period_row,
        controls=[
            ft.Icon(ft.Icons.DATE_RANGE, color=ft.Colors.ORANGE_400, size=20),
            ft.Text("Desde:", color=AppTheme.TEXT_SECONDARY),
            ft.TextButton(
                content=ft.Text(ref=period_start_text, value=period_start.strftime("%d/%m/%Y")),
                on_click=open_period_start_picker,
            ),
            ft.Text("Hasta:", color=AppTheme.TEXT_SECONDARY),
            ft.TextButton(
                content=ft.Text(ref=period_end_text, value=period_end.strftime("%d/%m/%Y")),
                on_click=open_period_end_picker,
            ),
        ],
        spacing=8,
        visible=False,
    )
    
    # Initial content
    initial_content = build_stats_content(selected_date, selected_date, True)
    
    return ft.Column(
        controls=[
            header_row,
            daily_date_row,
            period_selector_row,
            ft.Divider(height=15),
            ft.Column(
                ref=content_container,
                controls=initial_content,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
        ],
        expand=True,
    )
