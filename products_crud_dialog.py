import flet as ft
from database import get_all_products, insert_product, delete_product, update_product


def products_crud_dialog(page, on_refresh):
    selected_product = {"id": None}

    nombre = ft.TextField(label="Nombre")
    precio = ft.TextField(label="Precio", keyboard_type=ft.KeyboardType.NUMBER)
    cantidad = ft.TextField(label="Cantidad", keyboard_type=ft.KeyboardType.NUMBER)

    products_list = ft.Column(scroll=ft.ScrollMode.AUTO)

    def load_products():
        products_list.controls.clear()
        for p in get_all_products():
            products_list.controls.append(
                ft.Container(
                    padding=10,
                    bgcolor=ft.Colors.GREY_700,
                    border_radius=8,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(p["name"], color=ft.Colors.WHITE),
                            ft.Row(
                                controls=[
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT,
                                        on_click=lambda e, prod=p: select_product(prod)
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE,
                                        icon_color=ft.Colors.RED,
                                        on_click=lambda e, pid=p["id"]: delete(pid)
                                    ),
                                ]
                            )
                        ]
                    )
                )
            )
        page.update()

    def select_product(p):
        selected_product["id"] = p["id"]
        nombre.value = p["name"]
        precio.value = str(int(p["price"]))
        cantidad.value = str(p["cantidad_disponible"])
        page.update()

    def save(e):
        if selected_product["id"]:
            update_product(
                selected_product["id"],
                nombre.value,
                float(precio.value),
                int(cantidad.value)
            )
        else:
            insert_product(
                nombre.value,
                float(precio.value),
                None,
                int(cantidad.value)
            )

        clear_form()
        load_products()
        on_refresh()

    def delete(pid):
        delete_product(pid)
        load_products()
        on_refresh()

    def clear_form():
        selected_product["id"] = None
        nombre.value = ""
        precio.value = ""
        cantidad.value = ""

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Administrar productos"),
        content=ft.Column(
            width=500,
            controls=[
                products_list,
                ft.Divider(),
                nombre,
                precio,
                cantidad,
            ]
        ),
        actions=[
            ft.TextButton("Cerrar", on_click=lambda e: close()),
            ft.ElevatedButton("Guardar", on_click=save),
        ],
    )

    def open():
        load_products()
        dialog.open = True
        page.update()

    def close():
        dialog.open = False
        page.update()

    page.overlay.append(dialog)
    return open
