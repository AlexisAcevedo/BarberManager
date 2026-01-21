"""
Sidebar navigation component for Barber Manager.
Creates a NavigationRail with Spanish labels.
"""
import asyncio
import inspect
import flet as ft
from typing import Callable, Union


def create_sidebar(
    page: ft.Page,
    selected_index: int,
    on_change: Callable[[int], None]
) -> ft.NavigationRail:
    """
    Create the main navigation sidebar.
    
    Args:
        page: Flet page instance
        selected_index: Currently selected destination index
        on_change: Callback when selection changes (sync or async)
        
    Returns:
        NavigationRail component
    """
    
    def handle_change(e: ft.ControlEvent):
        result = on_change(e.control.selected_index)
        # If the callback returns a coroutine, schedule it
        if asyncio.iscoroutine(result):
            asyncio.create_task(result)
    
    rail = ft.NavigationRail(
        selected_index=selected_index,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=200,
        extended=True,
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
        leading=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(
                        ft.Icons.CONTENT_CUT,
                        size=40,
                        color=ft.Colors.BLUE_400
                    ),
                    ft.Text(
                        "Barber Manager",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_400
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5
            ),
            padding=ft.padding.only(bottom=20, top=10)
        ),
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
    
    return rail
