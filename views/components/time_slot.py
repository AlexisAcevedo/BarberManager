"""
Time Slot Component.
A reusable chip for displaying and selecting time slots.
"""
import flet as ft
from typing import Callable, Optional


def create_time_slot(
    time: str,
    is_available: bool,
    is_selected: bool,
    on_click: Optional[Callable[[str], None]] = None,
) -> ft.Container:
    """
    Create a time slot chip component.
    
    Args:
        time: Time string (e.g., "12:00")
        is_available: Whether the slot is available for booking
        is_selected: Whether this slot is currently selected
        on_click: Callback function(time) when clicked
        
    Returns:
        ft.Container: The styled time slot chip
    """
    # Determine colors based on state
    if is_selected:
        bgcolor = ft.Colors.GREEN_700
        text_color = ft.Colors.WHITE
    elif is_available:
        bgcolor = ft.Colors.BLUE_800
        text_color = ft.Colors.WHITE
    else:
        bgcolor = ft.Colors.with_opacity(0.1, ft.Colors.WHITE)
        text_color = ft.Colors.GREY_600
    
    # Determine tooltip
    if is_selected:
        tooltip = "Horario seleccionado"
    elif is_available:
        tooltip = "Click para seleccionar"
    else:
        tooltip = "No disponible - conflicto con otro turno"
    
    return ft.Container(
        content=ft.Text(
            time,
            size=14,
            color=text_color,
        ),
        padding=ft.padding.symmetric(horizontal=15, vertical=8),
        border_radius=8,
        bgcolor=bgcolor,
        on_click=(lambda e: on_click(time)) if (is_available and on_click) else None,
        ink=is_available,
        tooltip=tooltip,
        data={"time": time, "available": is_available},
    )


def update_time_slot_style(
    chip: ft.Container,
    is_selected: bool,
) -> None:
    """
    Update the visual style of an existing time slot chip.
    
    Args:
        chip: The container to update
        is_selected: Whether this slot should show as selected
    """
    if not chip.data:
        return
    
    is_available = chip.data.get("available", False)
    
    if is_selected:
        chip.bgcolor = ft.Colors.GREEN_700
    elif is_available:
        chip.bgcolor = ft.Colors.BLUE_800
    else:
        chip.bgcolor = ft.Colors.with_opacity(0.1, ft.Colors.WHITE)
