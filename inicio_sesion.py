import flet as ft
from database import validar_licencia

def mostrar_login(page: ft.Page, on_success):

    usuario_input = ft.TextField(label="Usuario")
    password_input = ft.TextField(label="Contraseña", password=True)

    mensaje = ft.Text("", color=ft.colors.RED)

    def intentar_login(e):
        ok, msg = validar_licencia(usuario_input.value, password_input.value)

        if ok:
            dialog.open = False
            page.update()
            on_success()
        else:
            mensaje.value = msg
            page.update()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Inicio de sesión"),
        content=ft.Column(
            tight=True,
            controls=[
                usuario_input,
                password_input,
                mensaje
            ]
        ),
        actions=[
            ft.ElevatedButton("Ingresar", on_click=intentar_login)
        ]
    )

    page.overlay.append(dialog)
    dialog.open = True
    page.update()
