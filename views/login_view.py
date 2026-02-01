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
        content=ft.Column(
            controls=[
                ft.Icon(ft.Icons.CONTENT_CUT, size=80, color=AppTheme.PRIMARY),
                ft.Text("Barber Manager Pro", size=32, weight=ft.FontWeight.BOLD, color=AppTheme.TEXT_PRIMARY),
                ft.Text("Identifícate para continuar", color=AppTheme.TEXT_SECONDARY),
                ft.Container(height=20),
                username_field,
                password_field,
                error_text,
                ft.Container(height=10),
                login_button
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        ),
        alignment=ft.Alignment(0, 0),
        expand=True,
        padding=40,
        bgcolor=AppTheme.BACKGROUND
    )
