import pandas as pd
from collections import defaultdict
from datetime import datetime


def generar_excel_ventas(rows_filtrados):
    """
    rows_filtrados viene del dashboard o de get_ventas_summary().
    Soporta dos formatos:
      - Formato get_ventas_summary(): nombre, unidades_vendidas, ingresos_totales
      - Formato dashboard detalle:    nombre, cantidad, subtotal/precio_unitario
    """

    if not rows_filtrados:
        return None

    agrupado = defaultdict(lambda: {
        "unidades": 0,
        "total": 0
    })

    for row in rows_filtrados:
        # Compatibilidad con sqlite3.Row (no soporta .get())
        if not isinstance(row, dict):
            row = dict(row)

        producto = row.get("nombre", "Desconocido")

        # Formato get_ventas_summary(): tiene unidades_vendidas e ingresos_totales
        if "unidades_vendidas" in row:
            unidades = row.get("unidades_vendidas") or 0
            total = row.get("ingresos_totales") or 0
        # Formato detalle de ventas: tiene cantidad y subtotal o precio_unitario
        else:
            unidades = row.get("cantidad") or 0
            total = row.get("subtotal") or (unidades * row.get("precio_unitario", 0))

        agrupado[producto]["unidades"] += unidades
        agrupado[producto]["total"] += total

    filas = []
    total_general = 0

    for producto, data in agrupado.items():
        filas.append({
            "Producto": producto,
            "Unidades vendidas": data["unidades"],
            "Total ($)": int(data["total"])
        })
        total_general += data["total"]

    filas.append({
        "Producto": "TOTAL GENERAL",
        "Unidades vendidas": "",
        "Total ($)": int(total_general)
    })

    df = pd.DataFrame(filas)

    fecha = datetime.now().strftime("%Y%m%d_%H%M")
    nombre_archivo = f"Ventas_Filtradas_{fecha}.xlsx"

    df.to_excel(nombre_archivo, index=False)

    return nombre_archivo