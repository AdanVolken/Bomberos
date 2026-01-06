import flet as ft
import os
import ventas
from collections import Counter
from database import (
    init_database,
    get_all_products,
    get_empresa,
    registrar_venta,
    insert_product
)


def main(page: ft.Page):
    page.title = "Mini POS"
    page.window_width = 1000
    page.window_height = 700
    page.padding = 20
    page.bgcolor = ft.Colors.RED_700

    # ------------------ INICIALIZAR BASE DE DATOS ------------------

    if not os.path.exists("Sistema_Tickets_DB.db"):
        init_database()
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Base de datos inicializada."),
            bgcolor=ft.Colors.ORANGE
        )
        page.snack_bar.open = True

    # ------------------ CARGAR DATOS ------------------

    empresa = get_empresa()
    if empresa:
        page.title = empresa.get("nombre", "Mini POS")

    products = get_all_products()

    if not products:
        page.add(
            ft.Container(
                expand=True,
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            "No hay productos cargados",
                            size=20,
                            weight="bold",
                            color=ft.Colors.WHITE
                        ),
                        ft.Text(
                            "Agregá productos con el botón",
                            color=ft.Colors.WHITE70
                        )
                    ]
                )
            )
        )

    cart = []

    # ------------------ GRID PRODUCTOS ------------------

    products_grid = ft.GridView(
        expand=True,
        runs_count=4,
        max_extent=180,
        spacing=10,
        run_spacing=10,
    )

    def refresh_products():
        products_grid.controls.clear()
        for product in get_all_products():
            products_grid.controls.append(create_product_card(product))
        page.update()

    # ------------------ VENTA ------------------

    cart_list = ft.Column(scroll=ft.ScrollMode.AUTO)
    total_text = ft.Text("Total: $0", size=16, weight="bold", color=ft.Colors.WHITE)

    def update_cart():
        cart_list.controls.clear()
        total = 0

        for item in cart:
            cart_list.controls.append(
                ft.Text(
                    f"{item['name']} - ${int(item['price'])}",
                    color=ft.Colors.WHITE
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
            page.update()
            return

        empresa_info = empresa if empresa else {"nombre": "Mini POS"}
        tickets = ventas.crear_tickets(cart, empresa_info)

        # Imprimir tickets (por ahora consola)
        for ticket in tickets:
            texto = ventas.generar_texto_ticket(ticket)
            print("\n--- TICKET ---")
            print(texto)
            print("--------------\n")
            # printer.print(texto)  ← futuro

        # Registrar ventas en DB
        product_counts = Counter()
        for item in cart:
            product_counts[item["id"]] += 1

        for product_id, cantidad in product_counts.items():
            registrar_venta(producto_id=product_id, cantidad=cantidad)

        cart.clear()
        update_cart()

        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"{len(tickets)} ticket(s) generado(s)"),
            bgcolor=ft.Colors.GREEN
        )
        page.snack_bar.open = True
        page.update()

    # ------------------ POPUP AGREGAR PRODUCTO ------------------

    nombre_input = ft.TextField(label="Nombre del producto")
    precio_input = ft.TextField(label="Precio", keyboard_type=ft.KeyboardType.NUMBER)

    def close_dialog(e=None):
        dialog.open = False
        page.update()

    def save_product(e):
        if not nombre_input.value or not precio_input.value:
            return

        insert_product(
            nombre=nombre_input.value,
            precio=float(precio_input.value),
            imagen=None
        )

        nombre_input.value = ""
        precio_input.value = ""
        close_dialog()
        refresh_products()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Agregar producto"),
        content=ft.Column(
            tight=True,
            controls=[nombre_input, precio_input]
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
        image_path = product.get("image")
        if image_path and os.path.exists(image_path):
            image_widget = ft.Image(
                src=image_path,
                fit=ft.ImageFit.COVER,
                width=180,
                height=180,
            )
        else:
            image_widget = ft.Container(
                width=180,
                height=180,
                bgcolor=ft.Colors.WHITE_30,
            )

        return ft.Container(
            width=180,
            height=180,
            border_radius=10,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            on_click=lambda e: add_to_cart(product),
            content=ft.Stack(
                controls=[
                    image_widget,
                    ft.Container(
                        padding=10,
                        content=ft.Column(
                            alignment=ft.MainAxisAlignment.END,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=5,
                            controls=[
                                ft.Container(
                                    padding=5,
                                    bgcolor=ft.Colors.BLACK_54,
                                    border_radius=5,
                                    content=ft.Text(
                                        product["name"],
                                        weight="bold",
                                        size=14,
                                        text_align="center",
                                        color=ft.Colors.WHITE,
                                    ),
                                ),
                                ft.Container(
                                    padding=5,
                                    bgcolor=ft.Colors.RED_700,
                                    border_radius=5,
                                    content=ft.Text(
                                        f"${int(product['price'])}",
                                        size=16,
                                        weight="bold",
                                        color=ft.Colors.WHITE,
                                    ),
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    # Cargar productos iniciales
    refresh_products()

    # ------------------ LAYOUT ------------------

    left_panel = ft.Column(
        expand=True,
        controls=[
            ft.Text("Productos", size=18, weight="bold", color=ft.Colors.WHITE),
            ft.ElevatedButton(
                "+ Agregar producto",
                on_click=open_add_product_dialog,
                bgcolor=ft.Colors.WHITE,
                color=ft.Colors.RED_700,
            ),
            products_grid,
        ],
    )

    right_panel = ft.Container(
        width=300,
        padding=10,
        bgcolor=ft.Colors.BLACK_54,
        border_radius=10,
        content=ft.Column(
            expand=True,
            controls=[
                ft.Text("Venta actual", size=18, weight="bold", color=ft.Colors.WHITE),
                ft.Divider(color=ft.Colors.WHITE),
                cart_list,
                ft.Divider(color=ft.Colors.WHITE),
                total_text,
                ft.ElevatedButton(
                    "Imprimir ticket",
                    on_click=lambda e: finalize_venta(),
                    bgcolor=ft.Colors.RED_700,
                    color=ft.Colors.WHITE,
                    width=280,
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
