import flet as ft
import hashlib
from database import get_connection

def mostrar_admin_cuentas(page: ft.Page):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, cliente, max_maquinas FROM licencia")
    usuarios = cursor.fetchall()
    conn.close()

    lista = ft.Column(scroll=ft.ScrollMode.AUTO)

    for u in usuarios:
        cliente = u["cliente"]
        max_maquinas = u["max_maquinas"]

        nuevo_cupo = ft.TextField(
            label="Máquinas",
            value=str(max_maquinas),
            width=100
        )

        nueva_pass = ft.TextField(
            label="Nueva contraseña",
            password=True,
            width=150
        )

        def guardar(e, cliente=cliente, nuevo_cupo=nuevo_cupo, nueva_pass=nueva_pass):
            conn = get_connection()
            cursor = conn.cursor()

            if nuevo_cupo.value:
                cursor.execute(
                    "UPDATE licencia SET max_maquinas = ? WHERE cliente = ?",
                    (int(nuevo_cupo.value), cliente)
                )

            if nueva_pass.value:
                hash_pass = hashlib.sha256(nueva_pass.value.encode()).hexdigest()
                cursor.execute(
                    "UPDATE licencia SET password_hash = ? WHERE cliente = ?",
                    (hash_pass, cliente)
                )

            conn.commit()
            conn.close()

            page.snack_bar = ft.SnackBar(
                content=ft.Text("Cuenta actualizada"),
                bgcolor=ft.colors.GREEN
            )
            page.snack_bar.open = True
            page.update()

        lista.controls.append(
            ft.Row(
                controls=[
                    ft.Text(cliente, width=150),
                    nuevo_cupo,
                    nueva_pass,
                    ft.ElevatedButton("Guardar", on_click=guardar)
                ]
            )
        )

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Administración de cuentas"),
        content=ft.Container(width=600, height=400, content=lista),
        actions=[
            ft.TextButton("Cerrar", on_click=lambda e: cerrar())
        ]
    )

    def cerrar():
        dialog.open = False
        page.update()

    page.overlay.append(dialog)
    dialog.open = True
    page.update()
