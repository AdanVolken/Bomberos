import pandas as pd
from collections import defaultdict
from datetime import datetime


def generar_excel_ventas(rows_filtrados):
    """
    rows_filtrados viene del dashboard.
    Contiene:
    id, total, nombre, cantidad, medio
    """

    if not rows_filtrados:
        return None

    agrupado = defaultdict(lambda: {
        "unidades": 0,
        "total": 0
    })

    # Agrupar por producto (subtotal = cantidad * precio_unitario por línea)
    for row in rows_filtrados:
        producto = row["nombre"]
        subtotal = row.get("subtotal") or (row["cantidad"] * row.get("precio_unitario", 0))
        agrupado[producto]["unidades"] += row["cantidad"]
        agrupado[producto]["total"] += subtotal

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
