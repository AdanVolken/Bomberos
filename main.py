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
    page.title = "Mini POS"
    page.window_width = 1000
    page.window_height = 700
    page.padding = 20
    page.bgcolor = ft.Colors.GREY_900  # Gris oscuro

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
        runs_count=4,      # ← 4 columnas fijas
        spacing=20,
        run_spacing=20,
    )

    def refresh_products():
        products_grid.controls.clear()
        for product in get_all_products():
            products_grid.controls.append(create_product_card(product))
        page.update()

    # ------------------ VENTA ------------------

    cart_list = ft.Column(scroll=ft.ScrollMode.AUTO)
    total_text = ft.Text("Total: $0", size=20, weight="bold", color=ft.Colors.WHITE, text_align="center")

    def remove_from_cart(index):
        """Elimina un producto del carrito por su índice"""
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
                            text_align="center",
                            size=20,
                            expand=True
                        ),
                        ft.TextButton(
                            "Eliminar",
                            on_click=lambda e, idx=i: remove_from_cart(idx),
                            style=ft.ButtonStyle(
                                color=ft.Colors.RED_500,
                            ),
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
                # bgcolor=ft.Colors.GREY_700,  # Gris medio
            )

        return ft.Container(
            width=180,
            height=180,
            border=ft.border.only(
                top=ft.border.BorderSide(
                    4,
                    ft.Colors.BLACK_38,
                    ft.BorderStyle.SOLID
                )
            ),
            border_radius=15,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            bgcolor=ft.Colors.GREY_800,
            on_click=lambda e: add_to_cart(product),
            content=ft.Stack(
                controls=[
                    # Fondo / imagen
                    image_widget,

                    # Nombre centrado
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(0, 0),  # ← CENTRO REAL
                        padding=10,
                        content=ft.Text(
                            product["name"],
                            size=26,
                            weight="bold",
                            color=ft.Colors.WHITE,
                            text_align="center",
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ),

                    # Precio abajo
                    ft.Container(
                        alignment=ft.Alignment(0, 1),  # ← ABAJO CENTRADO
                        padding=12,
                        content=ft.Container(
                            padding=6,
                            width=150,
                            bgcolor=ft.Colors.GREY_500,
                            border_radius=8,
                            content=ft.Text(
                                f"${int(product['price'])}",
                                size=22,
                                weight="bold",
                                color=ft.Colors.WHITE,
                                text_align="center",
                            ),
                        ),
                    ),
                ],
            ),

        )


    # Cargar productos iniciales
    refresh_products()

    # ------------------ LAYOUT ------------------

    # ------------------ REPORTE DE VENTAS ------------------
    
    def exportar_excel_ventas():
        ventas = get_ventas_summary()
        archivo = generar_excel_ventas(ventas)

        if archivo:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Excel generado: {archivo}"),
                bgcolor=ft.Colors.GREEN
            )
            page.snack_bar.open = True
            page.update()

    def show_ventas_totales(e):
        """Muestra el reporte de ventas totales"""
        ventas = get_ventas_summary()
        
        # Crear contenido del reporte
        reporte_items = []
        total_general = 0
        
        for venta in ventas:
            if venta["unidades_vendidas"] > 0:
                total_producto = venta["ingresos_totales"]
                total_general += total_producto
                reporte_items.append(
                    ft.Container(
                        padding=10,
                        expand=True,
                        bgcolor=ft.Colors.GREY_700,
                        border_radius=5,
                        margin=5,
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    venta["nombre"],
                                    size=20,
                                    weight="bold",
                                    color=ft.Colors.WHITE
                                ),
                                ft.Text(
                                    f"Unidades vendidas: {venta['unidades_vendidas']}",
                                    size=20,
                                    color=ft.Colors.WHITE70
                                ),
                                ft.Text(
                                    f"Total: ${int(total_producto)}",
                                    size=20,
                                    weight="bold",
                                    color=ft.Colors.WHITE
                                ),
                            ]
                        )
                    )
                )
        
        if not reporte_items:
            reporte_items.append(
                ft.Text(
                    "No hay ventas registradas",
                    size=18,
                    color=ft.Colors.WHITE70
                )
            )
        else:
            reporte_items.append(
                ft.Divider(color=ft.Colors.GREY_600)
            )
            reporte_items.append(
                ft.Container(
                    padding=10,
                    bgcolor=ft.Colors.GREY_600,
                    border_radius=5,
                    content=ft.Text(
                        f"TOTAL GENERAL: ${int(total_general)}",
                        size=22,
                        weight="bold",
                        color=ft.Colors.WHITE,
                        text_align="center"
                    )
                )
            )
        
        def close_ventas_dialog(e):
            ventas_dialog.open = False
            page.update()
        
        ventas_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Ventas Totales", size=24, weight="bold"),
            content=ft.Container(
                width=500,
                height=400,
                content=ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    controls=reporte_items,
                    spacing=5
                )
            ),
            actions=[
                ft.ElevatedButton(
                    "Exportar Excel",
                    on_click=lambda e: exportar_excel_ventas(),
                    bgcolor=ft.Colors.GREY_600,
                    color=ft.Colors.WHITE,
                ),
                ft.TextButton("Cerrar", on_click=close_ventas_dialog),
            ],

            bgcolor=ft.Colors.GREY_900,
        )
        
        page.overlay.append(ventas_dialog)
        ventas_dialog.open = True
        page.update()

    left_panel = ft.Column(
        expand=True,
        controls=[
            ft.Text("Productos", size=44, weight="bold", color=ft.Colors.WHITE),
            ft.ElevatedButton(
                "+ Agregar producto",
                on_click=open_add_product_dialog,
                bgcolor=ft.Colors.GREY_700,  # Gris medio-oscuro
                color=ft.Colors.WHITE,
            ),
            products_grid,
        ],
    )

    right_panel = ft.Container(
        width=400,
        padding=10,
        bgcolor=ft.Colors.GREY_800,  # Gris oscuro
        border=ft.border.only(
            top=ft.border.BorderSide(4, ft.Colors.BLACK_38)
        ),
        border_radius=10,
        content=ft.Column(
            expand=True,
            controls=[
                ft.Text("Venta actual", size=22, weight="bold", color=ft.Colors.WHITE),
                ft.Divider(color=ft.Colors.GREY_600),  # Gris para el divisor
                cart_list,
                ft.Divider(color=ft.Colors.GREY_600),  # Gris para el divisor
                total_text,
                ft.ElevatedButton(
                    "Imprimir ticket",
                    on_click=lambda e: finalize_venta(),
                    bgcolor=ft.Colors.GREY_600,  # Gris medio-oscuro
                    color=ft.Colors.WHITE,
                    width=280,
                ),
            ],
        ),
    )

    # Header con botón de Ventas Totales
    header = ft.Row(
        controls=[
            ft.Container(expand=True),  # Espaciador
            ft.ElevatedButton(
                "Ventas Totales",
                on_click=show_ventas_totales,
                bgcolor=ft.Colors.GREY_700,
                color=ft.Colors.WHITE,
            ),
        ],
        alignment=ft.MainAxisAlignment.END,
    )

    page.add(
        ft.Column(
            expand=True,
            controls=[
                header,
                ft.Row(
                    expand=True,
                    controls=[left_panel, right_panel],
                )
            ]
        )
    )


ft.app(target=main)

#comentario para prueba