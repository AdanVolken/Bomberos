import flet as ft


def main(page: ft.Page):
    page.title = "Mini POS"
    page.window_width = 1000
    page.window_height = 700
    page.padding = 20

    # ------------------ DATOS HARDCODEADOS ------------------

    products = [
        {"name": "Coca Cola", "price": 1500},
        {"name": "Empanada", "price": 800},
        {"name": "Pizza", "price": 2500},
        {"name": "Agua", "price": 600},
        {"name": "Hamburguesa", "price": 3200},
        {"name": "Papas fritas", "price": 1200},
    ]

    cart = []

    # ------------------ GRID PRODUCTOS ------------------

    products_grid = ft.GridView(
        expand=True,
        runs_count=4,
        max_extent=160,
        spacing=10,
        run_spacing=10,
    )

    # ------------------ VENTA ------------------

    cart_list = ft.Column(scroll=ft.ScrollMode.AUTO)
    total_text = ft.Text("Total: $0", size=16, weight="bold")

    def update_cart():
        cart_list.controls.clear()
        total = 0

        for item in cart:
            cart_list.controls.append(
                ft.Text(f"{item['name']} - ${item['price']}")
            )
            total += item["price"]

        total_text.value = f"Total: ${total}"
        page.update()

    def add_to_cart(product):
        cart.append(product)
        update_cart()

    # ------------------ PRODUCT CARD ------------------

    def create_product_card(product):
        return ft.Container(
            width=150,
            height=150,
            padding=10,
            bgcolor=ft.Colors.WHITE_30,
            border_radius=10,
            on_click=lambda e: add_to_cart(product),
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(product["name"], weight="bold", text_align="center"),
                    ft.Text(f"${product['price']}"),
                ],
            ),
        )

    # Cargar productos hardcodeados
    for product in products:
        products_grid.controls.append(create_product_card(product))

    # ------------------ LAYOUT ------------------

    left_panel = ft.Column(
        expand=True,
        controls=[
            ft.Text("Productos", size=18, weight="bold"),
            products_grid,
        ],
    )

    right_panel = ft.Container(
        width=300,
        padding=10,
        bgcolor=ft.Colors.BLACK_45,
        border_radius=10,
        content=ft.Column(
            expand=True,
            controls=[
                ft.Text("Venta actual", size=18, weight="bold"),
                ft.Divider(),
                cart_list,
                ft.Divider(),
                total_text,
                ft.ElevatedButton(
                    "Imprimir ticket",
                    on_click=lambda e: print("Imprimir ticket"),
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
