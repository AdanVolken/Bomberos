from datetime import datetime

# ===== COMANDOS ESC/POS =====

FUENTE_GRANDE = "\x1d\x21\x21"      # Doble ancho + doble alto
FUENTE_NORMAL = "\x1d\x21\x00"

NEGRITA_ON = "\x1b\x45\x01"
NEGRITA_OFF = "\x1b\x45\x00"

CENTRO = "\x1b\x61\x01"
IZQUIERDA = "\x1b\x61\x00"

LINEA = "=" * 48
SEPARADOR = "-" * 48


def generar_ticket_ventas_totales(empresa_nombre, ventas_summary):
    """
    Genera un ticket ESC/POS con el resumen de ventas totales
    ventas_summary viene de get_ventas_summary()
    """

    total_general = 0

    ticket = (
        CENTRO +
        NEGRITA_ON + empresa_nombre + NEGRITA_OFF + "\n" +
        LINEA + "\n\n" +
        IZQUIERDA
    )

    for v in ventas_summary:
        if v["unidades_vendidas"] <= 0:
            continue

        total_producto = v["ingresos_totales"]
        total_general += total_producto

        ticket += (
            NEGRITA_ON + v["nombre"] + NEGRITA_OFF + "\n" +
            f"Cantidad: {v['unidades_vendidas']}\n" +
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
