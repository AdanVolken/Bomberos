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
    page.padding = 0  # Sin padding para maximizar espacio
    page.bgcolor = ft.Colors.GREY_900  # Gris oscuro
    
    # Calcular altura disponible para el grid
    # Altura ventana - padding page (0) - header (32) - título (28) - botón (28) - spacing (10) - padding panel (16)
    header_height = 32
    title_height = 28
    button_height = 28
    spacing_between = 10  # spacing entre título, botón y grid (5*2)
    panel_padding = 16  # padding del panel izquierdo (8*2)
    available_height = page.window_height - header_height - title_height - button_height - spacing_between - panel_padding

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

    # Calcular el tamaño de cada celda para que quepan exactamente 4 columnas y 3 filas
    # Panel izquierdo: ancho total - panel derecho (300) - padding page (0) - spacing row (6)
    right_panel_width = 300  # Reducido para dar más espacio a las tarjetas
    row_spacing = 6  # Reducido
    panel_width = page.window_width - right_panel_width - row_spacing
    grid_spacing = 5  # Espacio horizontal entre columnas (reducido para tarjetas más grandes)
    grid_run_spacing = 5  # Espacio vertical entre filas (reducido para tarjetas más grandes)
    
    # Calcular ancho disponible para el grid (después de padding del panel)
    # Reducir padding para dar más espacio a las tarjetas
    panel_padding_reduced = 12  # Reducido de 16 a 12
    grid_available_width = panel_width - panel_padding_reduced
    
    # Calcular ancho por celda para EXACTAMENTE 4 columnas
    # 4 columnas = 3 espacios entre columnas
    # ancho_total = 4 * celda + 3 * spacing
    # celda = (ancho_total - 3 * spacing) / 4
    cell_width = (grid_available_width - (3 * grid_spacing)) / 4
    
    # Calcular alto por celda para EXACTAMENTE 3 filas
    # 3 filas = 2 espacios entre filas
    # Reducir un poco el spacing_between para dar más altura
    available_height_adjusted = available_height + 5  # Añadir un poco más de altura
    cell_height = (available_height_adjusted - (2 * grid_run_spacing)) / 3
    
    # Usar el menor valor para mantener aspecto cuadrado
    # PERO asegurarnos de que el ancho mínimo sea suficiente para 4 columnas
    max_extent = min(cell_width, cell_height)
    
    # Aumentar el max_extent un 10% para hacer las tarjetas más grandes
    max_extent = max_extent * 1.10
    
    # Si el max_extent es menor que el ancho necesario para 4 columnas, ajustarlo
    min_width_for_4_cols = (grid_available_width - (3 * grid_spacing)) / 4
    if max_extent < min_width_for_4_cols:
        max_extent = min_width_for_4_cols * 1.10  # También aumentar este valor un 10%
    
    # Altura total del grid: 3 filas * altura_celda + 2 espacios entre filas
    grid_height = (3 * max_extent) + (2 * grid_run_spacing)
    
    products_grid = ft.GridView(
        runs_count=4,  # FORZAR exactamente 4 columnas
        max_extent=max_extent,  # Tamaño máximo de cada celda
        spacing=grid_spacing,
        run_spacing=grid_run_spacing,
        height=grid_height,  # Altura fija para mostrar exactamente 3 filas completas
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
                        ft.Container(
                            content=ft.Text(
                                "Eliminar",
                                color=ft.Colors.GREEN_500,
                                size=16,
                            ),
                            on_click=lambda e, idx=i: remove_from_cart(idx),
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            ink=True,  # Efecto de click
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
            )
            total += item["price"]

        total_text.value = f"Total: ${int(total)}"
        page.update()

    def add_to_cart(product):
        # Validar cantidad disponible
        cantidad_restante = product.get("cantidad_restante", 0)
        
        if cantidad_restante <= 0:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"No hay cantidad disponible para {product['name']}"),
                bgcolor=ft.Colors.RED
            )
            page.snack_bar.open = True
            page.update()
            return
        
        # Contar cuántas veces ya está este producto en el carrito
        cantidad_en_carrito = sum(1 for item in cart if item["id"] == product["id"])
        
        # Validar que no se exceda la cantidad disponible
        if cantidad_en_carrito >= cantidad_restante:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"No se puede agregar más. Cantidad disponible: {cantidad_restante}"),
                bgcolor=ft.Colors.RED
            )
            page.snack_bar.open = True
            page.update()
            return
        
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

        # Registrar ventas en DB con validación
        product_counts = Counter()
        for item in cart:
            product_counts[item["id"]] += 1

        errores = []
        for product_id, cantidad in product_counts.items():
            success, message = registrar_venta(producto_id=product_id, cantidad=cantidad)
            if not success:
                errores.append(message)

        if errores:
            # Si hay errores, mostrar mensaje y no limpiar el carrito
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Error: " + "; ".join(errores)),
                bgcolor=ft.Colors.RED
            )
            page.snack_bar.open = True
            page.update()
            return

        cart.clear()
        update_cart()
        refresh_products()  # Actualizar productos para reflejar nuevas cantidades

        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"{len(tickets)} ticket(s) generado(s)"),
            bgcolor=ft.Colors.GREEN
        )
        page.snack_bar.open = True
        page.update()

    # ------------------ POPUP AGREGAR PRODUCTO ------------------

    nombre_input = ft.TextField(label="Nombre del producto")
    precio_input = ft.TextField(label="Precio", keyboard_type=ft.KeyboardType.NUMBER)
    cantidad_disponible_input = ft.TextField(
        label="Cantidad disponible", 
        keyboard_type=ft.KeyboardType.NUMBER,
        value="0"
    )

    def close_dialog(e=None):
        dialog.open = False
        page.update()

    def save_product(e):
        if not nombre_input.value or not precio_input.value:
            return

        cantidad_disponible = int(cantidad_disponible_input.value) if cantidad_disponible_input.value else 0

        insert_product(
            nombre=nombre_input.value,
            precio=float(precio_input.value),
            imagen=None,
            cantidad_disponible=cantidad_disponible
        )

        nombre_input.value = ""
        precio_input.value = ""
        cantidad_disponible_input.value = "0"
        close_dialog()
        refresh_products()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Agregar producto"),
        content=ft.Column(
            tight=True,
            controls=[nombre_input, precio_input, cantidad_disponible_input]
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
                expand=True,
            )
        else:
            image_widget = ft.Container(
                expand=True,
                bgcolor=ft.Colors.GREY_700,  # Gris medio
            )

        cantidad_restante = product.get("cantidad_restante", 0)
        # Determinar color del borde según disponibilidad
        border_color = ft.Colors.GREEN_500 if cantidad_restante > 0 else ft.Colors.RED_500
        # Deshabilitar click si no hay disponibilidad
        on_click_handler = lambda e: add_to_cart(product) if cantidad_restante > 0 else None
        # Opacidad reducida si no hay disponibilidad
        opacity = 0.5 if cantidad_restante <= 0 else 1.0

        return ft.Container(
            border=ft.border.only(
                top=ft.border.BorderSide(4, border_color, ft.BorderStyle.SOLID)
            ),
            border_radius=15,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            bgcolor=ft.Colors.GREY_800,  # Gris oscuro para la tarjeta
            opacity=opacity,
            on_click=on_click_handler,
            content=ft.Stack(
                expand=True,
                controls=[
                    image_widget,
                    ft.Container(
                        padding=10,
                        expand=True,
                        content=ft.Column(
                            alignment=ft.MainAxisAlignment.END,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=5,
                            controls=[
                                ft.Container(
                                    padding=5,
                                    border_radius=5,
                                    content=ft.Text(
                                        product["name"],
                                        weight="bold",
                                        size=18,
                                        text_align="center",
                                        color=ft.Colors.WHITE,
                                    ),
                                ),
                                ft.Container(
                                    padding=5,
                                    bgcolor=ft.Colors.GREY_500,  # Gris medio
                                    border_radius=5,
                                    content=ft.Text(
                                        f"${int(product['price'])}",
                                        size=18,
                                        weight="bold",
                                        text_align="center",
                                        color=ft.Colors.WHITE,
                                    ),
                                ),
                                ft.Container(
                                    padding=3,
                                    bgcolor=ft.Colors.GREY_600,
                                    border_radius=3,
                                    content=ft.Text(
                                        f"Disponible: {cantidad_restante}" if cantidad_restante > 0 else "Agotado",
                                        size=11,
                                        text_align="center",
                                        color=ft.Colors.WHITE if cantidad_restante > 0 else ft.Colors.RED_300,
                                        weight="bold" if cantidad_restante <= 0 else None,
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
            title=ft.Text("Ventas Totales", size=24, weight="bold", color=ft.Colors.GREEN_500),
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
                ft.Container(
                    content=ft.Text(
                        "Cerrar",
                        color=ft.Colors.GREEN_500,
                        size=16,
                    ),
                    on_click=close_ventas_dialog,
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    ink=True,
                ),
            ],

            bgcolor=ft.Colors.GREY_900,
        )
        
        page.overlay.append(ventas_dialog)
        ventas_dialog.open = True
        page.update()

    left_panel = ft.Container(
        expand=True,
        padding=ft.padding.all(6),  # Reducido de 8 a 6 para más espacio
        content=ft.Column(
            expand=True,
            spacing=5,
            controls=[
                ft.Container(
                    content=ft.Text("Productos", size=24, weight="bold", color=ft.Colors.WHITE),
                    height=28,
                ),
                ft.Container(
                    content=ft.ElevatedButton(
                        "+ Agregar producto",
                        on_click=open_add_product_dialog,
                        bgcolor=ft.Colors.GREY_700,
                        color=ft.Colors.WHITE,
                        height=28,
                    ),
                    height=28,
                ),
                ft.Container(
                    content=products_grid,
                    height=grid_height,  # Altura fija calculada para mostrar exactamente 3 filas completas
                    width=grid_available_width,  # Ancho fijo para forzar 4 columnas
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,  # Cortar contenido que exceda
                ),
            ],
        ),
    )

    right_panel = ft.Container(
        width=300,  # Ancho reducido para dar más espacio a las tarjetas
        padding=8,
        bgcolor=ft.Colors.GREY_800,  # Gris oscuro
        border=ft.border.only(
            left=ft.border.BorderSide(2, ft.Colors.GREY_600)
        ),
        content=ft.Column(
            expand=True,
            spacing=6,
            controls=[
                ft.Container(
                    content=ft.Text("Venta actual", size=18, weight="bold", color=ft.Colors.WHITE),
                    height=24,
                ),
                ft.Divider(color=ft.Colors.GREY_600, height=1),
                ft.Container(
                    content=cart_list,
                    expand=True,  # Expandir para usar el espacio disponible
                ),
                ft.Divider(color=ft.Colors.GREY_600, height=1),
                ft.Container(
                    content=total_text,
                    height=30,
                ),
                ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            "Imprimir ticket",
                            on_click=lambda e: finalize_venta(),
                            bgcolor=ft.Colors.GREY_600,
                            color=ft.Colors.WHITE,
                            width=280,
                            height=36,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
        ),
    )

    # Header con botón de Ventas Totales
    header = ft.Container(
        height=32,  # Altura reducida
        content=ft.Row(
            controls=[
                ft.Container(expand=True),  # Espaciador
                ft.ElevatedButton(
                    "Ventas Totales",
                    on_click=show_ventas_totales,
                    bgcolor=ft.Colors.GREY_700,
                    color=ft.Colors.WHITE,
                    height=28,
                ),
            ],
            alignment=ft.MainAxisAlignment.END,
        ),
        padding=ft.padding.only(bottom=3),
    )

    page.add(
        ft.Column(
            expand=True,
            spacing=0,
            controls=[
                header,
                ft.Container(
                    expand=True,
                    content=ft.Row(
                        expand=True,
                        spacing=10,
                        controls=[left_panel, right_panel],
                    ),
                ),
            ]
        )
    )


ft.app(target=main)

#comentario para prueba