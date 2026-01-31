"""
Componente de navegación lateral para Barber Manager.
Crea un NavigationRail con etiquetas en español y botón de logout.
"""
import asyncio
import flet as ft
from typing import Callable, Optional


def create_sidebar(
    page: ft.Page,
    selected_index: int,
    on_change: Callable[[int], None],
    on_logout: Optional[Callable[[], None]] = None
) -> ft.Column:
    """
    Crea el sidebar de navegación principal con botón de logout.
    
    Args:
        page: Instancia de página Flet
        selected_index: Índice de destino actualmente seleccionado
        on_change: Callback cuando cambia la selección (sync o async)
        on_logout: Callback cuando el usuario cierra sesión
        
    Retorna:
        Column con NavigationRail y botón de logout
    """
    
    def handle_change(e: ft.ControlEvent):
        result = on_change(e.control.selected_index)
        # Si el callback retorna una corrutina, programarla
        if asyncio.iscoroutine(result):
            asyncio.create_task(result)
    
    def handle_logout(e):
        if on_logout:
            on_logout()
    
    rail = ft.NavigationRail(
        selected_index=selected_index,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        extended=True,
        bgcolor=ft.Colors.TRANSPARENT,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
                selected_icon=ft.Icons.CALENDAR_MONTH,
                label="Agenda",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.PEOPLE_OUTLINED,
                selected_icon=ft.Icons.PEOPLE,
                label="Clientes",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.PERSON_OUTLINED,
                selected_icon=ft.Icons.PERSON,
                label="Barberos",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.ANALYTICS_OUTLINED,
                selected_icon=ft.Icons.ANALYTICS,
                label="Reportes",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.CUT_OUTLINED,
                selected_icon=ft.Icons.CUT,
                label="Servicios",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Configuración",
            ),
        ],
        on_change=handle_change,
    )
    
    # Header con logo
    header = ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(
                    ft.Icons.CONTENT_CUT,
                    size=40,
                    color="#10B981"
                ),
                ft.Text(
                    "Barber Manager",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color="#10B981"
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5
        ),
        padding=ft.padding.only(bottom=20, top=10)
    )
    
    # Botón de logout
    logout_button = ft.Container(
        content=ft.TextButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.LOGOUT, color=ft.Colors.RED_400, size=20),
                    ft.Text("Cerrar Sesión", color=ft.Colors.RED_400, size=12),
                ],
                spacing=8,
            ),
            on_click=handle_logout,
        ),
        padding=ft.padding.only(bottom=20, left=10, right=10),
    )
    
    # Contenedor completo del sidebar
    return ft.Column(
        controls=[
            header,
            ft.Container(content=rail, expand=True),
            logout_button,
        ],
        expand=True,
        spacing=0,
    )
