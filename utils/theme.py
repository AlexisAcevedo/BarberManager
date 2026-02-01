"""
Configuración de tema y paleta de colores para Barber Manager.
"""
import flet as ft

class AppTheme:
    """
    Colores y estilos predefinidos.
    """
    # Colores Principales
    PRIMARY = "#10B981"  # Emerald Green
    PRIMARY_DARK = "#059669"
    BACKGROUND = "#111827"  # Gray 900
    SURFACE = "#1F2937"     # Gray 800
    
    # Textos
    TEXT_PRIMARY = ft.Colors.WHITE
    TEXT_SECONDARY = ft.Colors.GREY_500
    TEXT_ERROR = ft.Colors.RED_400
    
    # Bordes
    BORDER_DEFAULT = ft.Colors.GREY_700
    BORDER_FOCUS = PRIMARY
    
    # Botones
    BTN_TEXT = ft.Colors.WHITE
    
    @classmethod
    def get_theme(cls):
        """Retorna la configuración de tema para Flet."""
        return ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=cls.PRIMARY,
                background=cls.BACKGROUND,
                surface=cls.SURFACE,
                error=cls.TEXT_ERROR,
            )
        )
