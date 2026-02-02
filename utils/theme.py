"""
Configuración de tema y paleta de colores para Barber Manager.
"""
import flet as ft

class AppTheme:
    """
    Colores y estilos predefinidos (Estilo Liquid Glass).
    """
    # Colores Principales
    PRIMARY = "#3B82F6"      # Electric Blue (Confianza, Profesionalismo)
    PRIMARY_DARK = "#1D4ED8"
    SECONDARY = "#60A5FA"
    
    ACCENT = "#F97316"       # Orange (CTA, Acción)
    
    # Fondos (Dark Mode Profundo)
    BACKGROUND = "#0F172A"   # Deep Slate
    SURFACE = "#1E293B"      # Slate 800
    
    # Glassmorphism
    GLASS_LOW = ft.Colors.with_opacity(0.05, ft.Colors.WHITE)
    GLASS_MEDIUM = ft.Colors.with_opacity(0.1, ft.Colors.WHITE)
    GLASS_HIGH = ft.Colors.with_opacity(0.2, ft.Colors.WHITE)
    BLUR_DEFAULT = 10
    
    # Textos
    TEXT_PRIMARY = "#F8FAFC" # Slate 50
    TEXT_SECONDARY = "#94A3B8" # Slate 400
    TEXT_ERROR = "#EF4444"   # Red 500
    
    # Fuentes (Google Fonts)
    FONT_HEADING = "Fira Code"
    FONT_BODY = "Fira Sans"
    
    # Bordes
    BORDER_DEFAULT = ft.Colors.with_opacity(0.1, ft.Colors.WHITE)
    BORDER_FOCUS = PRIMARY
    
    # Botones
    BTN_TEXT = ft.Colors.WHITE
    
    @classmethod
    def get_theme(cls):
        """Retorna la configuración de tema para Flet."""
        return ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=cls.PRIMARY,
                secondary=cls.SECONDARY,
                surface=cls.SURFACE,
                error=cls.TEXT_ERROR,
                on_primary=cls.BTN_TEXT,
                on_surface=cls.TEXT_PRIMARY,
            ),
            font_family=cls.FONT_BODY,
        )
