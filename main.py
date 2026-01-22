"""
Barber Manager - Punto de Entrada Principal de la Aplicación

Aplicación de escritorio para gestión de turnos de barbería.
Construida con Flet (UI) y SQLAlchemy (ORM) usando arquitectura MVC.
"""
import flet as ft

from config import logger
from database import init_db
from views.components.sidebar import create_sidebar
from views.agenda_view import create_agenda_view
from views.new_appointment_view import create_new_appointment_view
from views.clients_view import create_clients_view
from views.reports_view import create_reports_view
from views.services_view import create_services_view
from views.settings_view import create_settings_view
from views.login_view import create_login_view
from views.change_password_view import create_change_password_view

async def main(page: ft.Page):
    """
    Punto de entrada principal de la aplicación (versión asíncrona).
    Configura la página, inicializa la base de datos y gestiona el enrutamiento.
    """
    # Inicializar base de datos
    init_db()
    
    # Configuración de la página
    page.title = "Barber Manager Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0a0a0f"
    page.padding = 0
    
    # Configuración de ventana
    page.window.width = 1280
    page.window.height = 780
    
    # Contenedor del área de contenido principal
    content_area = ft.Container(expand=True, padding=20)
    
    # Componentes del sidebar (ocultos inicialmente si no hay sesión)
    sidebar_container = ft.Container(visible=False)
    divider = ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE), visible=False)

    async def navigate_to_index(index: int):
        """Navega a la ruta correspondiente según el índice del menú."""
        routes = ["/", "/clients", "/reports", "/services", "/settings"]
        if 0 <= index < len(routes):
            await page.push_route(routes[index])

    def get_selected_index(route: str) -> int:
        """Obtiene el índice del menú según la ruta actual."""
        route_map = {"/": 0, "/clients": 1, "/reports": 2, "/services": 3, "/settings": 4}
        base_route = route.split("?")[0]
        return route_map.get(base_route, 0)

    def on_logout():
        """
        Callback ejecutado cuando el usuario cierra sesión.
        Limpia los datos de sesión y redirige al login.
        """
        logger.info("Usuario cerró sesión")
        if hasattr(page, 'data') and page.data is not None:
            page.data.clear()
        sidebar_container.visible = False
        divider.visible = False
        content_area.content = create_login_view(page, on_login_success)
        page.update()

    # Crear sidebar con callback de logout
    sidebar = create_sidebar(page=page, selected_index=0, on_change=navigate_to_index, on_logout=on_logout)
    sidebar_container.content = sidebar

    def on_login_success(user_data):
        """
        Callback ejecutado cuando el login es exitoso.
        Recibe user_data como diccionario para evitar DetachedInstanceError.
        """
        # Usar page.data para el estado de sesión (compatible con Flet 0.80.x)
        if not hasattr(page, 'data') or page.data is None:
            page.data = {}
        page.data["user_id"] = user_data["id"]
        page.data["is_logged_in"] = True
        page.data["barber_id"] = user_data["barber_id"]
        
        # Verificar si debe cambiar contraseña
        if user_data.get("must_change_password", False):
            content_area.content = create_change_password_view(page, user_data, on_password_changed)
            page.update()
            return
        
        sidebar_container.visible = True
        divider.visible = True
        content_area.content = create_agenda_view(page)
        page.update()
    
    def on_password_changed(user_data):
        """
        Callback ejecutado cuando el usuario cambia su contraseña.
        """
        username = user_data.get("username", user_data.get("id", "desconocido"))
        logger.info(f"Usuario {username} completó cambio de contraseña")
        sidebar_container.visible = True
        divider.visible = True
        content_area.content = create_agenda_view(page)
        page.update()

    async def route_change(e: ft.RouteChangeEvent):
        """
        Maneja los cambios de ruta de la aplicación.
        Verifica autenticación y carga la vista correspondiente.
        """
        try:
            route = page.route
            query_params = None
            
            if "?" in route:
                route, query_params = route.split("?", 1)

            # VERIFICACIÓN DE AUTENTICACIÓN
            # Usando page.data para el estado de sesión (compatible con Flet 0.80.x)
            is_logged_in = False
            if hasattr(page, 'data') and page.data is not None:
                is_logged_in = page.data.get("is_logged_in", False)
            
            if not is_logged_in:
                sidebar_container.visible = False
                divider.visible = False
                content_area.content = create_login_view(page, on_login_success)
                page.update()
                return

            # Asegurar que el sidebar sea visible si hay sesión
            sidebar_container.visible = True
            divider.visible = True
            sidebar.selected_index = get_selected_index(route)
            
            # Cargar la vista apropiada según la ruta
            if route == "/" or route == "":
                content_area.content = create_agenda_view(page)
            elif route == "/new_appointment":
                content_area.content = create_new_appointment_view(page, query_params)
            elif route == "/clients":
                content_area.content = create_clients_view(page)
            elif route == "/reports":
                content_area.content = create_reports_view(page)
            elif route == "/services":
                content_area.content = create_services_view(page)
            elif route == "/settings":
                content_area.content = create_settings_view(page)
            else:
                await page.push_route("/")
                return
            
            page.update()
        except (ValueError, KeyError, AttributeError) as ex:
            # Errores esperados de navegación (rutas inválidas, datos faltantes)
            logger.error(f"Error de navegación: {ex}")
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Error al cargar la página"),
                bgcolor=ft.Colors.RED_700
            )
            page.snack_bar.open = True
            page.update()
        except Exception as ex:
            # Errores inesperados - registrar y re-lanzar para debugging
            logger.exception("Error inesperado en route_change")
            import traceback
            logger.debug(traceback.format_exc())
            # Re-lanzar en desarrollo, mostrar mensaje genérico en producción
            if AppConfig.DEBUG:
                raise

    async def view_pop(e: ft.ViewPopEvent):
        """Maneja el evento de retroceso de navegación."""
        await page.push_route("/")
    
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # Layout principal
    main_layout = ft.Row(
        controls=[
            sidebar_container,
            divider,
            content_area
        ],
        expand=True,
        spacing=0
    )
    
    page.add(main_layout)
    
    # Inicializar la primera ruta manualmente
    await route_change(None)


if __name__ == "__main__":
    ft.run(main)
