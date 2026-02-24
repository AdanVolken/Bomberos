import flet as ft
from database import (
    get_connection,
    get_medios_pago,
)
from generar_pdf_ventas import generar_pdf_ventas
import os
from generarExcel import generar_excel_ventas
from generar_ticket_ventas import generar_ticket_ventas_totales
from printer import imprimir_ticket


def mostrar_dashboard(page: ft.Page):

    # ============================
    # LISTAS PARA FILTROS (con manejo de errores si faltan tablas)
    # ============================

    cortes = []
    productos = []
    medios = []
    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT id FROM cortes_caja ORDER BY id DESC")
            cortes = [str(r["id"]) for r in cursor.fetchall()]
        except Exception:
            cortes = []

        try:
            cursor.execute("SELECT nombre FROM productos ORDER BY nombre")
            productos = [r["nombre"] for r in cursor.fetchall()]
        except Exception:
            productos = []

        try:
            medios = get_medios_pago()
        except Exception:
            medios = []
    except Exception as e:
        print(f"[Dashboard] Error al cargar filtros: {e}")
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

    # ============================
    # ESTADO FILTROS
    # ============================

    filtro_producto = "Todos"
    filtro_medio = "Todos"
    filtro_corte = "Todos"

    # ============================
    # TARJETAS
    # ============================

    total_text = ft.Text(size=28, weight="bold", color=ft.colors.GREEN_400)
    unidades_text = ft.Text(size=28, weight="bold", color=ft.colors.BLUE_400)
    cantidad_ventas_text = ft.Text(size=28, weight="bold", color=ft.colors.ORANGE_400)
    promedio_text = ft.Text(size=28, weight="bold", color=ft.colors.PURPLE_400)
    corte_text = ft.Text(size=20, weight="bold", color=ft.colors.WHITE)

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

    # ============================
    # EVENTOS FILTROS
    # ============================

    def cambiar_producto(e):
        nonlocal filtro_producto
        filtro_producto = e.control.value
        recalcular()

    def cambiar_medio(e):
        nonlocal filtro_medio
        filtro_medio = e.control.value
        recalcular()

    def cambiar_corte(e):
        nonlocal filtro_corte
        filtro_corte = e.control.value
        recalcular()

    def exportar_excel():
        rows = obtener_datos_filtrados()
        archivo = generar_excel_ventas(rows)

        if archivo:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Excel generado: {archivo}"),
                bgcolor=ft.colors.GREEN
            )
            page.snack_bar.open = True
            page.update()

            try:
                import os
                os.startfile(archivo)
            except:
                pass

    def imprimir_resumen():
        rows = obtener_datos_filtrados()

        texto = generar_ticket_ventas_totales(
            "Bomberos Voluntarios de Humboldt",
            rows
        )

        ok, msg = imprimir_ticket(texto)

        page.snack_bar = ft.SnackBar(
            content=ft.Text("Resumen impreso" if ok else msg),
            bgcolor=ft.colors.GREEN if ok else ft.colors.RED
        )
        page.snack_bar.open = True
        page.update()

    def generar_pdf():
        rows = obtener_datos_filtrados()

        archivo = generar_pdf_ventas(rows)

        if not archivo:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("No hay datos para generar PDF"),
                bgcolor=ft.colors.RED
            )
        else:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("PDF generado correctamente"),
                bgcolor=ft.colors.GREEN
            )

            try:
                os.startfile(archivo)
            except:
                pass

        page.snack_bar.open = True
        page.update()

         
    # ============================
    # DROPDOWNS
    # ============================

    estilo_dropdown = ft.TextStyle(color=ft.colors.GREY_300)

    producto_dropdown = ft.Dropdown(
        label="Producto",
        width=200,
        value="Todos",
        text_style=estilo_dropdown,
        label_style=estilo_dropdown,
        options=[ft.dropdown.Option("Todos")] +
                [ft.dropdown.Option(p) for p in productos],
        on_select=cambiar_producto
    )

    medio_dropdown = ft.Dropdown(
        label="Medio de pago",
        width=200,
        value="Todos",
        text_style=estilo_dropdown,
        label_style=estilo_dropdown,
        options=[ft.dropdown.Option("Todos")] +
                [ft.dropdown.Option(m["nombre"]) for m in medios],
        on_select=cambiar_medio
    )

    corte_dropdown = ft.Dropdown(
        label="Corte de caja",
        width=200,
        value="Todos",
        text_style=estilo_dropdown,
        label_style=estilo_dropdown,
        options=[ft.dropdown.Option("Todos")] +
                [ft.dropdown.Option(c) for c in cortes],
        on_select=cambiar_corte
    )

    # ============================
    # TARJETAS UI
    # ============================

    def tarjeta(titulo, contenido):
        return ft.Container(
            padding=20,
            bgcolor=ft.colors.GREY_800,
            border_radius=12,
            content=ft.Column(
                controls=[
                    ft.Text(titulo, color=ft.colors.WHITE70),
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

    # ============================
    # BOTONES
    # ============================

    botones = ft.Row(
        spacing=20,
        controls=[
            ft.ElevatedButton(
                "Exportar Excel",
                bgcolor=ft.colors.GREEN_700,
                color=ft.colors.WHITE,
                on_click=lambda e: exportar_excel()
            ),
            ft.ElevatedButton(
                "Imprimir resumen",
                bgcolor=ft.colors.ORANGE_700,
                color=ft.colors.WHITE,
                on_click=lambda e: imprimir_resumen()
            ),
            ft.ElevatedButton(
                "Generar PDF",
                bgcolor=ft.colors.PURPLE_700,
                color=ft.colors.WHITE,
                on_click=lambda e: generar_pdf()
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
                color=ft.colors.WHITE
            ),

            ft.Divider(color=ft.colors.GREY_700),

            ft.Row(
                spacing=20,
                controls=[
                    producto_dropdown,
                    medio_dropdown,
                    corte_dropdown
                ]
            ),

            ft.Divider(color=ft.colors.GREY_700),

            tarjetas_row,

            ft.Divider(color=ft.colors.GREY_700),

            botones
        ]
    )

    dialog = ft.AlertDialog(
        modal=True,
        bgcolor=ft.colors.GREY_900,
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
                style=ft.ButtonStyle(color=ft.colors.WHITE70)
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
