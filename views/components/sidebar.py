"""
Componente de navegación lateral para Barber Manager.
Crea un NavigationRail con etiquetas en español y botón de logout.
"""
import asyncio
import flet as ft
from typing import Callable, Optional
from utils.theme import AppTheme


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
    
    # Header con logo y título
    header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.CONTENT_CUT,
                        size=24,
                        color=AppTheme.PRIMARY
                    ),
                    padding=8,
                    bgcolor=ft.Colors.with_opacity(0.1, AppTheme.PRIMARY),
                    border_radius=8,
                ),
                ft.Column(
                    controls=[
                        ft.Text(
                            "Barber Manager",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=AppTheme.TEXT_PRIMARY,
                            font_family=AppTheme.FONT_HEADING
                        ),
                        ft.Text(
                            "PRO EDITION",
                            size=10,
                            color=AppTheme.ACCENT,
                            weight=ft.FontWeight.W_600,
                        ),
                    ],
                    spacing=0
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=15
        ),
        padding=ft.padding.only(top=30, bottom=20),
    )
    
    rail = ft.NavigationRail(
        selected_index=selected_index,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=220, # Más ancho para elegancia
        extended=True,
        bgcolor=ft.Colors.TRANSPARENT, # Transparente para usar el glass del padre
        indicator_color=ft.Colors.with_opacity(0.1, AppTheme.PRIMARY), # Indicador sutil
        indicator_shape=ft.RoundedRectangleBorder(radius=12),
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
    
    # Botón de logout estilizado
    logout_button = ft.Container(
        content=ft.TextButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.LOGOUT, color=AppTheme.TEXT_ERROR, size=20),
                    ft.Text(
                        "Cerrar Sesión", 
                        color=AppTheme.TEXT_ERROR, 
                        size=14,
                        weight=ft.FontWeight.W_500
                    ),
                ],
                spacing=12,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            on_click=handle_logout,
            style=ft.ButtonStyle(
                overlay_color=ft.Colors.with_opacity(0.05, AppTheme.TEXT_ERROR),
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=15
            )
        ),
        padding=20,
    )
    
    # Contenedor Glassmorphism para todo el sidebar
    return ft.Container(
        content=ft.Column(
            controls=[
                header,
                ft.Divider(height=1, color=AppTheme.BORDER_DEFAULT),
                ft.Container(
                    content=rail, 
                    expand=True,
                    padding=ft.padding.symmetric(vertical=10)
                ),
                ft.Divider(height=1, color=AppTheme.BORDER_DEFAULT),
                logout_button,
            ],
            expand=True,
            spacing=0,
        ),
        width=250, # Ancho fijo para el sidebar glass
        bgcolor=AppTheme.GLASS_LOW,
        blur=ft.Blur(10, 10, ft.BlurTileMode.MIRROR), # Efecto Blur
        border=ft.border.only(right=ft.BorderSide(1, AppTheme.BORDER_DEFAULT)),
    )
