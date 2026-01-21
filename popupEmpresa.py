import flet as ft

def popup_empresa(page: ft.Page, on_save):
    """
    Popup modal para configurar Empresa y Caja.
    on_save(nombre_empresa, nombre_caja)
    """

    empresa_input = ft.TextField(
        label="Nombre de la empresa",
        autofocus=True,
        bgcolor=ft.Colors.GREY_700,
        color=ft.Colors.WHITE,
        label_style=ft.TextStyle(color=ft.Colors.WHITE70),
    )

    caja_input = ft.TextField(
        label="Nombre de la caja",
        bgcolor=ft.Colors.GREY_700,
        color=ft.Colors.WHITE,
        label_style=ft.TextStyle(color=ft.Colors.WHITE70),
    )

    error_text = ft.Text(
        "",
        color=ft.Colors.RED_400,
        size=14
    )

    def guardar(e):
        if not empresa_input.value or not caja_input.value:
            error_text.value = "Debes completar ambos campos"
            page.update()
            return

        on_save(
            empresa_input.value.strip(),
            caja_input.value.strip()
        )

        dialog.open = False
        page.update()

    dialog = ft.AlertDialog(
        modal=True,
        bgcolor=ft.Colors.GREY_800,
        title=ft.Text(
            "Configuración inicial",
            color=ft.Colors.WHITE,
            weight="bold",
            size=20
        ),
        content=ft.Column(
            tight=True,
            spacing=15,
            controls=[
                ft.Text(
                    "Antes de comenzar, configurá la empresa y la caja",
                    color=ft.Colors.WHITE70,
                    size=14
                ),
                empresa_input,
                caja_input,
                error_text
            ],
        ),
        actions=[
            ft.ElevatedButton(
                "Guardar",
                on_click=guardar,
                bgcolor=ft.Colors.GREEN_700,
                color=ft.Colors.WHITE,
                height=45
            )
        ],
    )

    page.overlay.append(dialog)
    dialog.open = True
    page.update()

    return dialog
