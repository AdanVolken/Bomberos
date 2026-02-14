import flet as ft
from database import (
    get_medios_pago,
    insert_medio_pago,
    toggle_medio_pago
)


def mostrar_admin_medios_pago(page: ft.Page, refresh_dropdown_callback):

    lista = ft.Column(scroll=ft.ScrollMode.AUTO)
    nuevo_nombre = ft.TextField(label="Nuevo medio de pago")

    def refrescar():
        lista.controls.clear()

        medios_actualizados = get_medios_pago(activos_only=False)

        for mp in medios_actualizados:

            lista.controls.append(
                ft.Row(
                    controls=[
                        ft.Text(mp["nombre"], expand=True),
                        ft.Switch(
                            value=bool(mp["activo"]),
                            on_change=lambda e, mp_id=mp["id"]:
                                cambiar_estado(mp_id, e.control.value)
                        )
                    ]
                )
            )

        page.update()

    def cambiar_estado(medio_id, estado):
        toggle_medio_pago(medio_id, 1 if estado else 0)
        refrescar()
        refresh_dropdown_callback()   # 🔥 actualiza dropdown principal

    def agregar_medio(e):
        if not nuevo_nombre.value:
            return

        insert_medio_pago(nuevo_nombre.value.strip())
        nuevo_nombre.value = ""

        refrescar()
        refresh_dropdown_callback()   # 🔥 actualiza dropdown principal

    def cerrar(e=None):
        dialog.open = False
        page.update()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Administrar medios de pago"),
        content=ft.Column(
            width=400,
            controls=[
                lista,
                ft.Divider(),
                nuevo_nombre,
                ft.ElevatedButton(
                    "Agregar",
                    on_click=agregar_medio
                )
            ]
        ),
        actions=[
            ft.TextButton("Cerrar", on_click=cerrar)
        ]
    )

    page.overlay.append(dialog)
    dialog.open = True
    refrescar()
    page.update()
