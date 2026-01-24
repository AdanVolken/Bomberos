import flet as ft
import os
from printer import imprimir_ticket
import ventas
from collections import Counter
from generarExcel import generar_excel_ventas
from products_crud_dialog import products_crud_dialog
from popupEmpresa import popup_empresa
#from generar_ticket_ventas import generar_texto_ticket_ventas
from generar_ticket_ventas import generar_ticket_ventas_totales
from database import (
    # init_database,
    get_all_products,
    get_empresa,
    registrar_venta,
    insert_product,
    get_ventas_summary,
    insert_empresa
)


def main(page: ft.Page):
    page.title = "Mini POS"
    page.window_width = 1000
    page.window_height = 700
    page.padding = 20
    page.bgcolor = ft.colors.GREY_900

    # ------------------ DB INIT ------------------

    # if not os.path.exists("Sistema_Tickets_DB.db"):
    #     init_database()
    #     page.snack_bar = ft.SnackBar(
    #         content=ft.Text("Base de datos inicializada."),
    #         bgcolor=ft.colors.ORANGE
    #     )
    #     page.snack_bar.open = True

    # ------------------ EMPRESA CONFIG ------------------

    empresa = get_empresa()
    popup_empresa_dialog = None


    def on_save_empresa(nombre_empresa, nombre_caja):
        insert_empresa(
            nombre=nombre_empresa,
            nombre_caja=nombre_caja,
            logo=None
        )

        if popup_empresa_dialog:
            popup_empresa_dialog.open = False

        nonlocal_empresa()
        page.update()


    def nonlocal_empresa():
        nonlocal empresa
        empresa = get_empresa()
        page.title = empresa["nombre"]

    if not empresa or not empresa.get("nombre_caja"):
        popup_empresa_dialog = popup_empresa(page, on_save_empresa)


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

    open_products_crud = products_crud_dialog(page, refresh_products)

    def descargar_excel_ventas(e):
        ventas_summary = get_ventas_summary()

        if not ventas_summary:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("No hay ventas para exportar"),
                bgcolor=ft.colors.RED
            )
            page.snack_bar.open = True
            page.update()
            return

        archivo = generar_excel_ventas(ventas_summary)

        if archivo:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Excel generado: {archivo}"),
                bgcolor=ft.colors.GREEN
            )
            page.snack_bar.open = True
            page.update()

            # Opcional: abrir automáticamente el archivo
            try:
                os.startfile(archivo)
            except:
                pass

    def imprimir_ticket_ventas_totales(e):
        ventas_summary = get_ventas_summary()

        # Filtramos solo productos vendidos
        ventas_filtradas = [
            v for v in ventas_summary if v["unidades_vendidas"] > 0
        ]

        if not ventas_filtradas:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("No hay ventas para imprimir"),
                bgcolor=ft.colors.RED
            )
            page.snack_bar.open = True
            page.update()
            return

        # Generamos el texto del ticket
        texto_ticket = generar_ticket_ventas_totales(
            "Bomberos Voluntarios de Humboldt",
            ventas_filtradas
        )

        ok, msg = imprimir_ticket(texto_ticket)

        if ok:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Ticket de ventas impreso correctamente"),
                bgcolor=ft.colors.GREEN
            )
        else:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error al imprimir: {msg}"),
                bgcolor=ft.colors.RED
            )

        page.snack_bar.open = True
        page.update()

    # ------------------ CART ------------------

    cart_list = ft.Column(scroll=ft.ScrollMode.AUTO)
    total_text = ft.Text("Total: $0", size=25, weight="bold", color=ft.colors.WHITE)


    ultimo_total_text = ft.Text(
    "Última venta: $0",
    size=22,
    weight="bold",
    color=ft.colors.WHITE70
    )

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
                            color=ft.colors.WHITE,
                            size=18,
                            expand=True,
                        ),
                        ft.Container(
                            bgcolor=ft.colors.RED_700,
                            border_radius=8,
                            padding=8,
                            content=ft.Text(
                                "Eliminar",
                                color=ft.colors.WHITE,
                                size=16,
                                weight="bold"
                            ),
                            on_click=lambda e, idx=i: remove_from_cart(idx),
                            ink=True,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
            )
            total += item["price"]

        total_text.value = f"Total: ${int(total):,}"
        page.update()

    def add_to_cart(product):
        cart.append(product)
        update_cart()

    def finalize_venta():

        total_venta_actual = sum(item["price"] for item in cart)
        if not cart:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("El carrito está vacío"),
                bgcolor=ft.colors.RED
            )
            page.snack_bar.open = True
            page.update()
            return

        # --- NUEVA LÓGICA: Un ticket por producto ---
        errores = 0
        
        for item in cart:
            # Aquí personalizamos el texto para cada ticket individual
            # Usamos item["name"] para que aparezca el nombre del producto
            texto_ticket = ventas.generar_texto_ticket(empresa["nombre"],empresa["nombre_caja"], f"{item['name']}")
            
            ok_print, msg_print = imprimir_ticket(texto_ticket)
            
            if ok_print : 
                registrar_venta(item["id"], 1)
            else:
                errores += 1

        if errores > 0:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error en {errores} ticket(s)"),
                bgcolor=ft.colors.RED
            )
        else:
            # Guardamos el total ANTES de limpiar
            ultimo_total_text.value = f"Última venta: ${int(total_venta_actual):,}"
            # Si todo salió bien, registramos la venta en DB y limpiamos
            # (Opcional: puedes registrar la venta antes del loop)
            cart.clear()
            update_cart()
            refresh_products() 

            page.snack_bar = ft.SnackBar(
                content=ft.Text("Todos los tickets impresos y cortados"),
                bgcolor=ft.colors.GREEN
            )
        
        page.snack_bar.open = True
        page.update()


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
    page.overlay.append(dialog)

    def open_add_product_dialog(e):
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
                                    color=ft.colors.WHITE,
                                    text_align="center",
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Text(
                                    f"Vendido: {product['cantidad_vendida']}",
                                    size=16,
                                    color=(
                                        ft.colors.RED_400
                                        if product["cantidad_disponible"] <= 5
                                        else ft.colors.WHITE70
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
                            bgcolor=ft.colors.GREY_500,
                            border_radius=8,
                            content=ft.Text(
                                f"${int(product['price'])}",
                                size=20,
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

    # ------------------ LAYOUT ------------------

    left_panel = ft.Column(
        expand=True,
        controls=[
            ft.Text("Productos", size=40, weight="bold", color=ft.colors.WHITE),

            # FILA DE BOTONES
            ft.Row(
                spacing=10,
                controls=[
                    ft.ElevatedButton(
                        "+ Agregar producto",
                        on_click=open_add_product_dialog,
                        bgcolor=ft.colors.GREY_700,
                        color=ft.colors.WHITE,
                    ),
                    ft.ElevatedButton(
                        "Descargar Excel",
                        on_click=descargar_excel_ventas,
                        bgcolor=ft.colors.GREEN_700,
                        color=ft.colors.WHITE,
                    ),
                    ft.ElevatedButton(
                        "Ticket ventas",
                        on_click=imprimir_ticket_ventas_totales, 
                        bgcolor=ft.colors.BLUE_700,
                        color=ft.colors.WHITE,
                    ),
                    ft.ElevatedButton(
                        "Administrar productos",
                        on_click=open_products_crud,
                        bgcolor=ft.colors.ORANGE_700,
                        color=ft.colors.WHITE,
                    ),
                    ft.ElevatedButton(
                        "Cambiar caja",
                        bgcolor=ft.colors.GREY_700,
                        color=ft.colors.WHITE,
                        on_click=lambda e: popup_empresa(
                            page,
                            on_save_empresa,
                            empresa
                        )
                    ),
                ],
            ),

            products_grid,
        ],
    )


    right_panel = ft.Container(
        width=350,
        padding=10,
        bgcolor=ft.colors.GREY_800,
        border_radius=10,
        content=ft.Column(
            expand=True,
            controls=[
                # TÍTULO
                ft.Text(
                    "Venta actual",
                    size=22,
                    weight="bold",
                    color=ft.colors.WHITE
                ),

                # LISTA DE PRODUCTOS (SCROLL)
                ft.Container(
                    expand=True,   #  ocupa todo el espacio disponible
                    content=cart_list
                ),

                # TOTAL (FIJO)
                total_text,
                # ÚLTIMA VENTA
                ultimo_total_text,

                # BOTÓN FIJO ABAJO
                ft.ElevatedButton(
                    "Imprimir ticket",
                    on_click=lambda e: finalize_venta(),
                    bgcolor=ft.colors.GREY_600,
                    color=ft.colors.WHITE,
                    height=55,   # ← agranda el botón
                    style=ft.ButtonStyle(
                        text_style=ft.TextStyle(
                            size=18,
                            weight="bold"
                        )
                    ),
                ),
            ]
        ),
    )

    page.add(
        ft.Row(
            expand=True,
            controls=[left_panel, right_panel],
        )
    )


ft.app(target=main)
