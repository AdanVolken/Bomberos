import flet as ft
import os
from printer import imprimir_ticket
import ventas
from collections import Counter
from generarExcel import generar_excel_ventas
from database import (
    init_database,
    get_all_products,
    get_empresa,
    registrar_venta,
    insert_product,
    get_ventas_summary
)


def main(page: ft.Page):
    page.title = "Mini POS"
    page.window_width = 1000
    page.window_height = 700
    page.padding = 20
    page.bgcolor = ft.Colors.GREY_900

    # ------------------ DB INIT ------------------

    if not os.path.exists("Sistema_Tickets_DB.db"):
        init_database()
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Base de datos inicializada."),
            bgcolor=ft.Colors.ORANGE
        )
        page.snack_bar.open = True

    # ------------------ LOAD DATA ------------------

    empresa = get_empresa()
    if empresa:
        page.title = empresa.get("nombre", "Mini POS")

    cart = []

    # ------------------ GRID ------------------

    products_grid = ft.GridView(
        expand=True,
        runs_count=4,
        spacing=20,
        run_spacing=20,
    )

    def refresh_products():
        products_grid.controls.clear()
        for product in get_all_products():
            products_grid.controls.append(create_product_card(product))
        page.update()

    def descargar_excel_ventas(e):
        ventas_summary = get_ventas_summary()

        if not ventas_summary:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("No hay ventas para exportar"),
                bgcolor=ft.Colors.RED
            )
            page.snack_bar.open = True
            page.update()
            return

        archivo = generar_excel_ventas(ventas_summary)

        if archivo:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Excel generado: {archivo}"),
                bgcolor=ft.Colors.GREEN
            )
            page.snack_bar.open = True
            page.update()

            # Opcional: abrir automáticamente el archivo
            try:
                os.startfile(archivo)
            except:
                pass


    # ------------------ CART ------------------

    cart_list = ft.Column(scroll=ft.ScrollMode.AUTO)
    total_text = ft.Text("Total: $0", size=20, weight="bold", color=ft.Colors.WHITE)

    def remove_from_cart(index):
        if 0 <= index < len(cart):
            cart.pop(index)
            update_cart()

    def update_cart():
        cart_list.controls.clear()
        total = 0

        for i, item in enumerate(cart):
            cart_list.controls.append(
                ft.Row(
                    controls=[
                        ft.Text(
                            f"{item['name']} - ${int(item['price'])}",
                            color=ft.Colors.WHITE,
                            size=18,
                            expand=True,
                        ),
                        ft.Container(
                            content=ft.Text(
                                "Eliminar",
                                color=ft.Colors.RED_500,
                                size=16,
                            ),
                            on_click=lambda e, idx=i: remove_from_cart(idx),
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            ink=True,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
            )
            total += item["price"]

        total_text.value = f"Total: ${int(total)}"
        page.update()

    def add_to_cart(product):
        cart.append(product)
        update_cart()

    def finalize_venta():
        if not cart:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("El carrito está vacío"),
                bgcolor=ft.Colors.RED
            )
            page.snack_bar.open = True
            return

        empresa_info = empresa if empresa else {"nombre": "Mini POS"}
        tickets = ventas.crear_tickets(cart, empresa_info)

        product_counts = Counter()
        for item in cart:
            product_counts[item["id"]] += 1

        texto_ticket = ventas.generar_texto_ticket(cart, total_text.value)

        ok_print, msg_print = imprimir_ticket(texto_ticket)

        if not ok_print:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(msg_print),
                bgcolor=ft.Colors.RED
            )
            page.snack_bar.open = True
            return


        cart.clear()
        update_cart()
        refresh_products() 

        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"{len(tickets)} ticket(s) generado(s)"),
            bgcolor=ft.Colors.GREEN
        )
        page.snack_bar.open = True

    # ------------------ ADD PRODUCT ------------------

    nombre_input = ft.TextField(label="Nombre del producto")
    precio_input = ft.TextField(label="Precio", keyboard_type=ft.KeyboardType.NUMBER)
    cantidad_input = ft.TextField(
        label="Cantidad disponible",
        keyboard_type=ft.KeyboardType.NUMBER
    )

    def close_dialog(e=None):
        dialog.open = False
        page.update()

    def save_product(e):
        if not nombre_input.value or not precio_input.value or not cantidad_input.value:
            return

        insert_product(
            nombre=nombre_input.value,
            precio=float(precio_input.value),
            imagen=None,
            cantidad_disponible=int(cantidad_input.value)
        )

        nombre_input.value = ""
        precio_input.value = ""
        cantidad_input.value = ""

        close_dialog()
        refresh_products()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Agregar producto"),
        content=ft.Column(
            tight=True,
            controls=[nombre_input, precio_input, cantidad_input]
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=close_dialog),
            ft.ElevatedButton("Guardar", on_click=save_product),
        ],
    )

    def open_add_product_dialog(e):
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # ------------------ PRODUCT CARD ------------------

    def create_product_card(product):
        return ft.Container(
            width=180,
            height=180,
            border_radius=15,
            bgcolor=ft.Colors.GREY_800,
            on_click=lambda e: add_to_cart(product),
            content=ft.Stack(
                controls=[
                    # CONTENIDO CENTRAL (Nombre + Stock)
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(0, 0),  # centro
                        content=ft.Column(
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=6,
                            controls=[
                                ft.Text(
                                    product["name"],
                                    size=30,
                                    weight="bold",
                                    color=ft.Colors.WHITE,
                                    text_align="center",
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Text(
                                    f"Stock: {product['cantidad_disponible']}",
                                    size=16,
                                    color=(
                                        ft.Colors.RED_400
                                        if product["cantidad_disponible"] <= 5
                                        else ft.Colors.WHITE70
                                    ),
                                ),
                            ],
                        ),
                    ),

                    # PRECIO ABAJO
                    ft.Container(
                        alignment=ft.Alignment(0, 1),
                        padding=10,
                        content=ft.Container(
                            padding=6,
                            width=140,
                            bgcolor=ft.Colors.GREY_500,
                            border_radius=8,
                            content=ft.Text(
                                f"${int(product['price'])}",
                                size=20,
                                weight="bold",
                                color=ft.Colors.WHITE,
                                text_align="center",
                            ),
                        ),
                    ),
                ],
            ),

        )

    refresh_products()

    # ------------------ LAYOUT ------------------

    left_panel = ft.Column(
        expand=True,
        controls=[
            ft.Text("Productos", size=40, weight="bold", color=ft.Colors.WHITE),
            ft.ElevatedButton(
                "+ Agregar producto",
                on_click=open_add_product_dialog,
                bgcolor=ft.Colors.GREY_700,
                color=ft.Colors.WHITE,
            ),
            ft.ElevatedButton(
            "Descargar Excel de ventas",
            on_click=descargar_excel_ventas,
            bgcolor=ft.Colors.GREEN_700,
            color=ft.Colors.WHITE,
        ),
            products_grid,
        ],
    )

    right_panel = ft.Container(
        width=380,
        padding=10,
        bgcolor=ft.Colors.GREY_800,
        border_radius=10,
        content=ft.Column(
            expand=True,
            controls=[
                ft.Text("Venta actual", size=22, weight="bold", color=ft.Colors.WHITE),
                cart_list,
                total_text,
                ft.ElevatedButton(
                    "Imprimir ticket",
                    on_click=lambda e: finalize_venta(),
                    bgcolor=ft.Colors.GREY_600,
                    color=ft.Colors.WHITE,
                ),
            ],
        ),
    )

    page.add(
        ft.Row(
            expand=True,
            controls=[left_panel, right_panel],
        )
    )


ft.app(target=main)
