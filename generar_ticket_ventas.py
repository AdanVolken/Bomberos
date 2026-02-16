from datetime import datetime
from collections import defaultdict

# ===== COMANDOS ESC/POS =====

FUENTE_GRANDE = "\x1d\x21\x21"
FUENTE_NORMAL = "\x1d\x21\x00"

NEGRITA_ON = "\x1b\x45\x01"
NEGRITA_OFF = "\x1b\x45\x00"

CENTRO = "\x1b\x61\x01"
IZQUIERDA = "\x1b\x61\x00"

LINEA = "=" * 48
SEPARADOR = "-" * 48


def generar_ticket_ventas_totales(empresa_nombre, rows_filtrados):
    """
    rows_filtrados viene del dashboard.
    Contiene:
    id, total, nombre, cantidad, medio, corte_id
    """

    if not rows_filtrados:
        return "No hay datos para imprimir"

    # Agrupar por producto
    agrupado = defaultdict(lambda: {
        "unidades": 0,
        "total": 0
    })

    for row in rows_filtrados:
        producto = row["nombre"]
        agrupado[producto]["unidades"] += row["cantidad"]
        agrupado[producto]["total"] += row["total"]

    total_general = 0

    ticket = (
        CENTRO +
        NEGRITA_ON + empresa_nombre + NEGRITA_OFF + "\n" +
        LINEA + "\n\n" +
        IZQUIERDA
    )

    for producto, data in agrupado.items():
        if data["unidades"] <= 0:
            continue

        total_producto = data["total"]
        total_general += total_producto

        ticket += (
            NEGRITA_ON + producto + NEGRITA_OFF + "\n" +
            f"Cantidad: {data['unidades']}\n" +
            f"Total: ${int(total_producto):,}\n" +
            SEPARADOR + "\n"
        )

    ticket += (
        "\n" +
        LINEA + "\n" +
        CENTRO +
        NEGRITA_ON + FUENTE_GRANDE +
        f"TOTAL: ${int(total_general):,}" +
        FUENTE_NORMAL + NEGRITA_OFF + "\n\n" +
        FUENTE_NORMAL +
        datetime.now().strftime("%d/%m/%Y %H:%M") + "\n\n\n"
    )

    return ticket
