"""
Login view for Barber Manager.
Handles user authentication and session initiation.
"""
import flet as ft
from database import get_db
from services.auth_service import AuthService
from utils.theme import AppTheme


def create_login_view(page: ft.Page, on_login_success) -> ft.Control:
    """
    Create the login screen.
    """
    username_field = ft.TextField(
        label="Usuario",
        prefix_icon=ft.Icons.PERSON,
        border_color=AppTheme.BORDER_DEFAULT,
        focused_border_color=AppTheme.BORDER_FOCUS,
        on_submit=lambda _: password_field.focus(),
        color=AppTheme.TEXT_PRIMARY
    )
    
    password_field = ft.TextField(
        label="Contraseña",
        prefix_icon=ft.Icons.LOCK,
        password=True,
        can_reveal_password=True,
        border_color=AppTheme.BORDER_DEFAULT,
        focused_border_color=AppTheme.BORDER_FOCUS,
        on_submit=lambda _: do_login(None),
        color=AppTheme.TEXT_PRIMARY
    )
    
    error_text = ft.Text(color=AppTheme.TEXT_ERROR, size=12, visible=False)
    
    def do_login(e):
        username = username_field.value.strip()
        password = password_field.value.strip()
        
        if not username or not password:
            error_text.value = "Por favor ingrese usuario y contraseña"
            error_text.visible = True
            page.update()
            return
            
        with get_db() as db:
            user, error_msg = AuthService.authenticate(db, username, password)
            if user:
                # Extraer datos del usuario DENTRO de la sesión para evitar DetachedInstanceError
                user_data = {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role,
                    "barber_id": user.barber_id,
                    "must_change_password": getattr(user, 'must_change_password', False)
                }
                
                # Guardar datos de sesión usando page.data para Flet 0.80.x
                if not hasattr(page, 'data') or page.data is None:
                    page.data = {}
                page.data["user_id"] = user_data["id"]
                page.data["username"] = user_data["username"]
                page.data["role"] = user_data["role"]
                page.data["barber_id"] = user_data["barber_id"]
                
                # Pasar diccionario en lugar de objeto ORM
                on_login_success(user_data)
            else:
                error_text.value = error_msg or "Credenciales inválidas"
                error_text.visible = True
                page.update()

    login_button = ft.ElevatedButton(
        content=ft.Text("Iniciar Sesión", size=16, color=AppTheme.BTN_TEXT),
        width=300,
        height=50,
        style=ft.ButtonStyle(
            bgcolor=AppTheme.PRIMARY,
            color=AppTheme.BTN_TEXT,
            shape=ft.RoundedRectangleBorder(radius=8)
        ),
        on_click=do_login
    )

    return ft.Container(
        content=ft.Row(
            controls=[
                # Tarjeta de Login Glassmorphism
                ft.Container(
                    content=ft.Column(
                        controls=[
                            # Header
                            ft.Container(
                                content=ft.Icon(
                                    ft.Icons.CONTENT_CUT, 
                                    size=60, 
                                    color=AppTheme.ACCENT
                                ),
                                padding=20,
                                bgcolor=ft.Colors.with_opacity(0.1, AppTheme.ACCENT),
                                border_radius=50,
                                alignment=ft.Alignment(0, 0)
                            ),
                            ft.Container(height=10),
                            ft.Text(
                                "BARBER MANAGER", 
                                size=24, 
                                weight=ft.FontWeight.BOLD, 
                                color=AppTheme.TEXT_PRIMARY,
                                font_family=AppTheme.FONT_HEADING,
                                text_align=ft.TextAlign.CENTER
                            ),
                            ft.Text(
                                "PRO EDITION", 
                                size=12, 
                                color=AppTheme.PRIMARY, 
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER
                            ),
                            ft.Container(height=30),
                            
                            # Campos
                            ft.Text("Bienvenido de nuevo", color=AppTheme.TEXT_SECONDARY, size=14),
                            ft.Container(height=10),
                            username_field,
                            ft.Container(height=10),
                            password_field,
                            
                            ft.Container(height=20),
                            error_text,
                            ft.Container(height=10),
                            
                            login_button,
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=5
                    ),
                    width=400,
                    padding=40,
                    bgcolor=AppTheme.GLASS_LOW,
                    border_radius=20,
                    border=ft.border.all(1, AppTheme.BORDER_DEFAULT),
                    blur=ft.Blur(20, 20, ft.BlurTileMode.MIRROR),
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=50,
                        color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                        offset=ft.Offset(0, 20),
                    )
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        ),
        alignment=ft.Alignment(0, 0),
        expand=True,
        bgcolor=AppTheme.BACKGROUND # Color base
    )
