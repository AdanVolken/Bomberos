from datetime import datetime

# ===== COMANDOS ESC/POS =====

FUENTE_GRANDE = "\x1d\x21\x21"
FUENTE_NORMAL = "\x1d\x21\x00"

NEGRITA_ON = "\x1b\x45\x01"
NEGRITA_OFF = "\x1b\x45\x00"

CENTRO = "\x1b\x61\x01"
IZQUIERDA = "\x1b\x61\x00"

LINEA = "=" * 48
SEPARADOR = "-" * 48


def generar_ticket_corte(empresa_nombre, resumen_medios, total_general):
    """
    resumen_medios:
    [
        {"nombre": "Efectivo", "total": 50000},
        {"nombre": "Débito", "total": 32000}
    ]
    """

    ticket = (
        CENTRO +
        NEGRITA_ON + empresa_nombre + NEGRITA_OFF + "\n" +
        LINEA + "\n\n" +
        NEGRITA_ON + "CORTE DE CAJA" + NEGRITA_OFF + "\n\n" +
        IZQUIERDA
    )

    for r in resumen_medios:
        ticket += (
            NEGRITA_ON + r["nombre"] + NEGRITA_OFF + "\n" +
            f"Total: ${int(r['total']):,}\n" +
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
        datetime.now().strftime("%d/%m/%Y %H:%M") +
        "\n\n\n"
    )

    return ticket
