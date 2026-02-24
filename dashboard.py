import flet as ft
from database import get_connection, get_empresa
from generar_ticket_ventas import generar_ticket_ventas_totales
from printer import imprimir_ticket


def mostrar_dashboard(page: ft.Page):

    # Sin filtros: siempre "Todos"
    filtro_producto = "Todos"
    filtro_medio = "Todos"
    filtro_corte = "Todos"

    # ============================
    # TARJETAS
    # ============================

    total_text = ft.Text(size=28, weight="bold", color=ft.Colors.GREEN_400)
    unidades_text = ft.Text(size=28, weight="bold", color=ft.Colors.BLUE_400)
    cantidad_ventas_text = ft.Text(size=28, weight="bold", color=ft.Colors.ORANGE_400)
    promedio_text = ft.Text(size=28, weight="bold", color=ft.Colors.PURPLE_400)
    corte_text = ft.Text(size=20, weight="bold", color=ft.Colors.WHITE)

    # ============================
    # CONSULTA FILTRADA
    # ============================

    def obtener_datos_filtrados():
        try:
            conn = get_connection()
            cursor = conn.cursor()

            query = """
            SELECT v.id, v.total, p.nombre, d.cantidad, d.precio_unitario,
                   (d.cantidad * d.precio_unitario) as subtotal,
                   m.nombre as medio
            FROM ventas v
            JOIN ventas_detalle d ON v.id = d.venta_id
            JOIN productos p ON d.producto_id = p.id
            JOIN medios_pago m ON v.medio_pago_id = m.id
            """

            condiciones = []
            valores = []

            if filtro_producto != "Todos":
                condiciones.append("p.nombre = ?")
                valores.append(filtro_producto)

            if filtro_medio != "Todos":
                condiciones.append("m.nombre = ?")
                valores.append(filtro_medio)

            if filtro_corte != "Todos":
                condiciones.append("v.corte_id = ?")
                valores.append(int(filtro_corte))

            if condiciones:
                query += " WHERE " + " AND ".join(condiciones)

            cursor.execute(query, valores)
            # Convertir a dict para que .get() funcione en los generadores de reportes
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
            return rows
        except Exception as e:
            print(f"[Dashboard] Error en obtener_datos_filtrados: {e}")
            try:
                conn.close()
            except Exception:
                pass
            return []

    # ============================
    # RECALCULAR TARJETAS
    # ============================

    def recalcular():

        rows = obtener_datos_filtrados()

        # Total: sumar el total de cada venta una sola vez (cada venta tiene varias filas por detalle)
        totales_por_venta = {}
        for r in rows:
            vid = r["id"]
            if vid not in totales_por_venta:
                totales_por_venta[vid] = r["total"]
        total = sum(totales_por_venta.values())

        unidades = sum(r["cantidad"] for r in rows)
        cantidad_ventas = len(totales_por_venta)
        promedio = total / cantidad_ventas if cantidad_ventas > 0 else 0

        total_text.value = f"${int(total):,}"
        unidades_text.value = str(unidades)
        cantidad_ventas_text.value = str(cantidad_ventas)
        promedio_text.value = f"${int(promedio):,}"
        corte_text.value = f"Corte: {filtro_corte}"

        page.update()

    def imprimir_resumen():
        rows = obtener_datos_filtrados()
        empresa = get_empresa()
        nombre_empresa = (empresa.get("nombre") or "Mi Empresa").strip() or "Mi Empresa"

        texto = generar_ticket_ventas_totales(
            nombre_empresa,
            rows
        )

        ok, msg = imprimir_ticket(texto)

        page.snack_bar = ft.SnackBar(
            content=ft.Text("Resumen impreso" if ok else msg),
            bgcolor=ft.Colors.GREEN if ok else ft.Colors.RED
        )
        page.snack_bar.open = True
        page.update()

    # ============================
    # TARJETAS UI
    # ============================

    def tarjeta(titulo, contenido):
        return ft.Container(
            padding=20,
            bgcolor=ft.Colors.GREY_800,
            border_radius=12,
            content=ft.Column(
                controls=[
                    ft.Text(titulo, color=ft.Colors.WHITE70),
                    contenido
                ]
            )
        )

    tarjetas_row = ft.Row(
        spacing=20,
        controls=[
            tarjeta("Total vendido", total_text),
            tarjeta("Unidades vendidas", unidades_text),
            tarjeta("Cantidad ventas", cantidad_ventas_text),
            tarjeta("Promedio por venta", promedio_text),
            tarjeta("Corte actual", corte_text),
        ]
    )

    # Solo botón Imprimir resumen
    botones = ft.Row(
        spacing=20,
        controls=[
            ft.ElevatedButton(
                "Imprimir resumen",
                bgcolor=ft.Colors.ORANGE_700,
                color=ft.Colors.WHITE,
                on_click=lambda e: imprimir_resumen()
            ),
        ]
    )

    # ============================
    # LAYOUT
    # ============================

    contenido = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            ft.Text(
                "Dashboard de Ventas",
                size=30,
                weight="bold",
                color=ft.Colors.WHITE
            ),

            ft.Divider(color=ft.Colors.GREY_700),

            tarjetas_row,

            ft.Divider(color=ft.Colors.GREY_700),

            botones
        ]
    )

    dialog = ft.AlertDialog(
        modal=True,
        bgcolor=ft.Colors.GREY_900,
        content=ft.Container(
            width=1100,
            height=650,
            padding=20,
            content=contenido
        ),
        actions=[
            ft.TextButton(
                "Cerrar",
                on_click=lambda e: cerrar(),
                style=ft.ButtonStyle(color=ft.Colors.WHITE70)
            )
        ]
    )

    def cerrar():
        dialog.open = False
        page.update()

    page.overlay.append(dialog)
    dialog.open = True

    recalcular()
    page.update()
