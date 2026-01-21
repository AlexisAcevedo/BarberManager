"""
Login view for Barber Manager.
Handles user authentication and session initiation.
"""
import flet as ft
from database import get_db
from services.auth_service import AuthService


def create_login_view(page: ft.Page, on_login_success) -> ft.Control:
    """
    Create the login screen.
    """
    username_field = ft.TextField(
        label="Usuario",
        prefix_icon=ft.Icons.PERSON,
        border_color=ft.Colors.GREY_700,
        focused_border_color=ft.Colors.BLUE_400,
        on_submit=lambda _: password_field.focus()
    )
    
    password_field = ft.TextField(
        label="Contraseña",
        prefix_icon=ft.Icons.LOCK,
        password=True,
        can_reveal_password=True,
        border_color=ft.Colors.GREY_700,
        focused_border_color=ft.Colors.BLUE_400,
        on_submit=lambda _: do_login(None)
    )
    
    error_text = ft.Text(color=ft.Colors.RED_400, size=12, visible=False)
    
    def do_login(e):
        username = username_field.value.strip()
        password = password_field.value.strip()
        
        if not username or not password:
            error_text.value = "Por favor ingrese usuario y contraseña"
            error_text.visible = True
            page.update()
            return
            
        with get_db() as db:
            user = AuthService.authenticate(db, username, password)
            if user:
                # Save session data using page.data for Flet 0.80.x
                if not hasattr(page, 'data') or page.data is None:
                    page.data = {}
                page.data["user_id"] = user.id
                page.data["username"] = user.username
                page.data["role"] = user.role
                page.data["barber_id"] = user.barber_id
                
                on_login_success(user)
            else:
                error_text.value = "Credenciales inválidas"
                error_text.visible = True
                page.update()

    login_button = ft.ElevatedButton(
        content=ft.Text("Iniciar Sesión", size=16),
        width=300,
        height=50,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=8)
        ),
        on_click=do_login
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(ft.Icons.PASSWORD_ROUNDED, size=80, color=ft.Colors.BLUE_400),
                ft.Text("Barber Manager Pro", size=32, weight=ft.FontWeight.BOLD),
                ft.Text("Identifícate para continuar", color=ft.Colors.GREY_500),
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
        padding=40
    )
