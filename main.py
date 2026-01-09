import flet as ft
import os
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
    # ------------------ PAGE SETUP ------------------
    page.title = "Mini POS"
    page.window_width = 1000
    page.window_height = 700
    page.padding = 20
    page.bgcolor = ft.colors.GREY_900

    # ------------------ DB INIT ------------------
    if not os.path.exists("Sistema_Tickets_DB.db"):
        init_database()
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Base de datos inicializada."),
            bgcolor=ft.colors.ORANGE
        )
        page.snack_bar.open = True

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

    # ------------------ CART ------------------
    cart_list = ft.Column(scroll=ft.ScrollMode.AUTO)
    total_text = ft.Text("Total: $0", size=20, weight="bold", color=ft.colors.WHITE)

    def update_cart():
        cart_list.controls.clear()
        total = 0

        for item in cart:
            cart_list.controls.append(
                ft.Text(
                    f"{item['name']} - ${int(item['price'])}",
                    color=ft.colors.WHITE,
                    size=18
                )
            )
            total += item["price"]

        total_text.value = f"Total: ${int(total)}"
        page.update()

    def add_to_cart(product):
        if product["cantidad_disponible"] <= 0:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Sin stock disponible"),
                bgcolor=ft.colors.RED
            )
            page.snack_bar.open = True
            return

        cart.append(product)
        update_cart()

    def finalize_venta():
        if not cart:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("El carrito está vacío"),
                bgcolor=ft.colors.RED
            )
            page.snack_bar.open = True
            return

        product_counts = Counter()
        for item in cart:
            product_counts[item["id"]] += 1

        for product_id, cantidad in product_counts.items():
            ok, msg = registrar_venta(producto_id=product_id, cantidad=cantidad)
            if not ok:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(msg),
                    bgcolor=ft.colors.RED
                )
                page.snack_bar.open = True
                return

        cart.clear()
        update_cart()
        refresh_products()

        page.snack_bar = ft.SnackBar(
            content=ft.Text("Venta registrada correctamente"),
            bgcolor=ft.colors.GREEN
        )
        page.snack_bar.open = True

    # ------------------ ADD PRODUCT ------------------
    nombre_input = ft.TextField(label="Nombre")
    precio_input = ft.TextField(label="Precio", keyboard_type=ft.KeyboardType.NUMBER)
    cantidad_input = ft.TextField(label="Stock inicial", keyboard_type=ft.KeyboardType.NUMBER)

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
        dialog.open = False
        refresh_products()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Agregar producto"),
        content=ft.Column(controls=[nombre_input, precio_input, cantidad_input]),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: setattr(dialog, "open", False)),
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
            bgcolor=ft.colors.GREY_800,
            on_click=lambda e: add_to_cart(product),
            content=ft.Stack(
                controls=[
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Column(
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Text(
                                    product["name"],
                                    size=20,
                                    weight="bold",
                                    color=ft.colors.WHITE,
                                    text_align="center"
                                ),
                                ft.Text(
                                    f"Stock: {product['cantidad_disponible']}",
                                    color=ft.colors.RED_400
                                    if product["cantidad_disponible"] <= 5
                                    else ft.colors.WHITE70
                                ),
                            ],
                        ),
                    ),
                    ft.Container(
                        alignment=ft.Alignment(0, 1),
                        padding=10,
                        content=ft.Container(
                            padding=6,
                            width=140,
                            bgcolor=ft.colors.GREY_500,
                            border_radius=8,
                            content=ft.Text(
                                f"${int(product['price'])}",
                                size=18,
                                weight="bold",
                                color=ft.colors.WHITE,
                                text_align="center",
                            ),
                        ),
                    ),
                ],
            ),
        )

    refresh_products()

    # ------------------ VENTAS TOTALES ------------------
    def exportar_excel_ventas():
        archivo = generar_excel_ventas(get_ventas_summary())
        if archivo:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Excel generado: {archivo}"),
                bgcolor=ft.colors.GREEN
            )
            page.snack_bar.open = True

    def show_ventas_totales(e):
        ventas = get_ventas_summary()
        items = []
        total = 0

        for v in ventas:
            if v["unidades_vendidas"] > 0:
                total += v["ingresos_totales"]
                items.append(
                    ft.Text(
                        f"{v['nombre']} - {v['unidades_vendidas']} u - ${int(v['ingresos_totales'])}",
                        color=ft.colors.WHITE
                    )
                )

        items.append(ft.Divider())
        items.append(
            ft.Text(f"TOTAL: ${int(total)}", weight="bold", color=ft.colors.WHITE)
        )

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Ventas Totales"),
            content=ft.Column(controls=items, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.ElevatedButton("Exportar Excel", on_click=lambda e: exportar_excel_ventas()),
                ft.TextButton("Cerrar", on_click=lambda e: setattr(dialog, "open", False)),
            ],
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # ------------------ LAYOUT ------------------
    header = ft.Row(
        alignment=ft.MainAxisAlignment.END,
        controls=[
            ft.ElevatedButton(
                "Ventas Totales",
                on_click=show_ventas_totales,
                bgcolor=ft.colors.GREY_700,
                color=ft.colors.WHITE
            )
        ]
    )

    left_panel = ft.Column(
        expand=True,
        controls=[
            ft.Text("Productos", size=36, weight="bold", color=ft.colors.WHITE),
            ft.ElevatedButton("+ Agregar producto", on_click=open_add_product_dialog),
            products_grid,
        ],
    )

    right_panel = ft.Container(
        width=350,
        padding=10,
        bgcolor=ft.colors.GREY_800,
        border_radius=10,
        content=ft.Column(
            controls=[
                ft.Text("Venta actual", size=22, weight="bold", color=ft.colors.WHITE),
                cart_list,
                total_text,
                ft.ElevatedButton("Imprimir ticket", on_click=lambda e: finalize_venta()),
            ]
        ),
    )

    page.add(
        ft.Column(
            expand=True,
            controls=[
                header,
                ft.Row(expand=True, controls=[left_panel, right_panel])
            ]
        )
    )


ft.app(target=main)
