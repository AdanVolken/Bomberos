from datetime import datetime

# ===== Comandos ESC/POS =====

FUENTE_GRANDE = "\x1d\x21\x21"      # Doble ancho + doble alto
FUENTE_NORMAL = "\x1d\x21\x00"

NEGRITA_ON = "\x1b\x45\x03"
NEGRITA_OFF = "\x1b\x45\x00"

CENTRO = "\x1b\x61\x01"
IZQUIERDA = "\x1b\x61\x00"

LINEA = "=" * 48


def crear_tickets(productos, empresa):
    """
    Devuelve un ticket por producto
    """
    tickets = []
    for producto in productos:
        tickets.append({
            "empresa": empresa.get("nombre", "Sistema de Tickets"),
            "producto": producto["name"],
            "precio": producto["price"],
            "caja": empresa.get("nombre_caja", "Caja 1"),
        })
    return tickets


def generar_texto_ticket(empresa,caja, producto):
    """
    Genera texto ESC/POS listo para imprimir
    """

    ticket = (
        CENTRO +

        # Empresa
        NEGRITA_ON + empresa + NEGRITA_OFF + "\n" +
        LINEA + "\n" +

        # Producto (grande)
        NEGRITA_ON + FUENTE_GRANDE + producto + FUENTE_NORMAL + NEGRITA_OFF + "\n" +

        LINEA + "\n" +
        NEGRITA_ON + caja + NEGRITA_OFF + "\n" +
        # Mensaje final
        "Gracias por su compra\n" +

        # Espacio para corte
        "\n"
    )

    return ticket
