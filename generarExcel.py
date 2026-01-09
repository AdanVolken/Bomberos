import pandas as pd
from datetime import datetime


def generar_excel_ventas(ventas_summary):
    """
    ventas_summary: lista de dicts con claves:
    nombre, unidades_vendidas, ingresos_totales
    """

    if not ventas_summary:
        return None

    filas = []
    total_general = 0

    for venta in ventas_summary:
        if venta["unidades_vendidas"] > 0:
            total = venta["ingresos_totales"]
            total_general += total

            filas.append({
                "Producto": venta["nombre"],
                "Unidades vendidas": venta["unidades_vendidas"],
                "Stock": venta["stock_actual"],
                "Total ($)": int(total)
            })

    filas.append({
        "Producto": "TOTAL GENERAL",
        "Unidades vendidas": "",
        "Total ($)": int(total_general)
    })

    df = pd.DataFrame(filas)

    nombre_archivo = f"Ventas_Bomberos.xlsx"
    df.to_excel(nombre_archivo, index=False)

    return nombre_archivo

# Ejemplo de uso