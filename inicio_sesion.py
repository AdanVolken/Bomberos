import flet as ft
from database import validar_licencia

def mostrar_login(page: ft.Page, on_success):
    """
    Muestra un popup de inicio de sesión obligatorio.
    Retorna el usuario logueado a través de on_success(usuario)
    """
    mensaje = ft.Text(
        "",
        color=ft.Colors.RED_400,
        size=13,
        text_align=ft.TextAlign.CENTER
    )

    def intentar_login(e):
        usuario = usuario_input.value.strip() if usuario_input.value else ""
        password = password_input.value.strip() if password_input.value else ""

        # Caso especial: usuario admin
        if usuario == "admin" and password == "daleboca":
            dialog.open = False
            page.update()
            on_success("admin")
            return

        # Para otros usuarios, validar contra la base de datos
        ok, msg = validar_licencia(usuario, password)

        if ok:
            dialog.open = False
            page.update()
            on_success(usuario)
        else:
            mensaje.value = msg
            page.update()

    usuario_input = ft.TextField(
        label="Usuario",
        autofocus=True,
        width=300,
        bgcolor=ft.Colors.GREY_700,
        color=ft.Colors.WHITE,
        label_style=ft.TextStyle(color=ft.Colors.WHITE70),
        border_color=ft.Colors.GREY_600,
        focused_border_color=ft.Colors.BLUE_400,
        text_align=ft.TextAlign.CENTER,
        on_submit=intentar_login
    )
    
    password_input = ft.TextField(
        label="Contraseña",
        password=True,
        width=300,
        bgcolor=ft.Colors.GREY_700,
        color=ft.Colors.WHITE,
        label_style=ft.TextStyle(color=ft.Colors.WHITE70),
        border_color=ft.Colors.GREY_600,
        focused_border_color=ft.Colors.BLUE_400,
        text_align=ft.TextAlign.CENTER,
        on_submit=intentar_login
    )

    dialog = ft.AlertDialog(
        modal=True,
        bgcolor=ft.Colors.GREY_800,
        title=ft.Container(
            content=ft.Text(
                "Inicio de sesión",
                color=ft.Colors.WHITE,
                weight="bold",
                size=24,
                text_align=ft.TextAlign.CENTER
            ),
            alignment=ft.Alignment(0, 0),
            padding=ft.padding.only(bottom=10)
        ),
        content=ft.Container(
            content=ft.Column(
                spacing=20,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    usuario_input,
                    password_input,
                    mensaje
                ]
            ),
            padding=20,
            width=350
        ),
        actions=[
            ft.Container(
                content=ft.ElevatedButton(
                    "Ingresar",
                    on_click=intentar_login,
                    bgcolor=ft.Colors.GREEN_700,
                    color=ft.Colors.WHITE,
                    height=45,
                    width=200
                ),
                alignment=ft.Alignment(0, 0),
                padding=ft.padding.only(top=10)
            )
        ],
        actions_alignment=ft.MainAxisAlignment.CENTER
    )

    page.overlay.append(dialog)
    dialog.open = True
    page.update()
