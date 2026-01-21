"""
Vista de cambio de contraseña para Barber Manager.
Se muestra cuando el usuario debe cambiar su contraseña por primera vez.
"""
import flet as ft
from database import get_db
from services.auth_service import AuthService
from config import logger


def create_change_password_view(page: ft.Page, user_data: dict, on_password_changed) -> ft.Control:
    """
    Crea la vista de cambio de contraseña obligatorio.
    
    Args:
        page: Instancia de página Flet
        user_data: Diccionario con datos del usuario (id, username, etc.)
        on_password_changed: Callback cuando se cambia la contraseña exitosamente
        
    Retorna:
        Control de la vista
    """
    
    # Extraer datos del diccionario
    user_id = user_data["id"]
    username = user_data["username"]
    
    current_password_field = ft.TextField(
        label="Contraseña Actual",
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        password=True,
        can_reveal_password=True,
        border_color=ft.Colors.GREY_700,
        focused_border_color=ft.Colors.BLUE_400,
    )
    
    new_password_field = ft.TextField(
        label="Nueva Contraseña",
        prefix_icon=ft.Icons.LOCK,
        password=True,
        can_reveal_password=True,
        border_color=ft.Colors.GREY_700,
        focused_border_color=ft.Colors.BLUE_400,
    )
    
    confirm_password_field = ft.TextField(
        label="Confirmar Nueva Contraseña",
        prefix_icon=ft.Icons.LOCK_CLOCK,
        password=True,
        can_reveal_password=True,
        border_color=ft.Colors.GREY_700,
        focused_border_color=ft.Colors.BLUE_400,
    )
    
    error_text = ft.Text(color=ft.Colors.RED_400, size=12, visible=False)
    success_text = ft.Text(color=ft.Colors.GREEN_400, size=12, visible=False)
    
    def validate_password(password: str) -> tuple[bool, str]:
        """Valida que la contraseña cumpla requisitos mínimos."""
        if len(password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"
        return True, ""
    
    def do_change_password(e):
        current = current_password_field.value.strip()
        new_password = new_password_field.value.strip()
        confirm = confirm_password_field.value.strip()
        
        # Validaciones
        if not current or not new_password or not confirm:
            error_text.value = "Por favor complete todos los campos"
            error_text.visible = True
            success_text.visible = False
            page.update()
            return
        
        if new_password != confirm:
            error_text.value = "Las contraseñas no coinciden"
            error_text.visible = True
            success_text.visible = False
            page.update()
            return
        
        is_valid, msg = validate_password(new_password)
        if not is_valid:
            error_text.value = msg
            error_text.visible = True
            success_text.visible = False
            page.update()
            return
        
        if new_password == current:
            error_text.value = "La nueva contraseña debe ser diferente a la actual"
            error_text.visible = True
            success_text.visible = False
            page.update()
            return
        
        # Verificar contraseña actual y cambiar
        with get_db() as db:
            # Re-obtener usuario desde la base de datos para tener sesión activa
            from models.base import User
            db_user = db.query(User).filter(User.id == user_id).first()
            
            if not db_user:
                error_text.value = "Error: usuario no encontrado"
                error_text.visible = True
                page.update()
                return
            
            # Verificar contraseña actual
            if not AuthService.verify_password(current, db_user.password_hash):
                error_text.value = "Contraseña actual incorrecta"
                error_text.visible = True
                success_text.visible = False
                page.update()
                return
            
            # Cambiar contraseña
            success, error = AuthService.change_password(db, user_id, new_password)
            
            if success:
                logger.info(f"Usuario {username} cambió su contraseña")
                # Pasar diccionario con datos del usuario
                on_password_changed({"id": user_id, "username": username})
            else:
                error_text.value = error or "Error al cambiar contraseña"
                error_text.visible = True
                success_text.visible = False
                page.update()
    
    change_button = ft.ElevatedButton(
        content=ft.Text("Cambiar Contraseña", size=16),
        width=300,
        height=50,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE_700,
            color=ft.Colors.WHITE,
            shape=ft.RoundedRectangleBorder(radius=8)
        ),
        on_click=do_change_password
    )
    
    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Icon(ft.Icons.SECURITY, size=80, color=ft.Colors.ORANGE_400),
                ft.Text("Cambio de Contraseña", size=28, weight=ft.FontWeight.BOLD),
                ft.Text(
                    "Por seguridad, debes cambiar tu contraseña",
                    color=ft.Colors.GREY_500,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.Container(height=20),
                current_password_field,
                new_password_field,
                confirm_password_field,
                error_text,
                success_text,
                ft.Container(height=10),
                change_button,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            width=350
        ),
        alignment=ft.Alignment(0, 0),
        expand=True,
        padding=40
    )
