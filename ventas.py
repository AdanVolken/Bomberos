from datetime import datetime

# ===== Comandos ESC/POS =====

FUENTE_GRANDE = "\x1d\x21\x11"      # Doble ancho + doble alto
FUENTE_NORMAL = "\x1d\x21\x00"

NEGRITA_ON = "\x1b\x45\x01"
NEGRITA_OFF = "\x1b\x45\x00"

CENTRO = "\x1b\x61\x01"
IZQUIERDA = "\x1b\x61\x00"

LINEA = "=" * 24


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
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        })
    return tickets


def generar_texto_ticket(empresa, producto):
    """
    Genera texto ESC/POS listo para imprimir
    """

    ticket = (
        CENTRO +

        # Empresa
        NEGRITA_ON + empresa + NEGRITA_OFF + "\n" +
        LINEA + "\n\n" +

        # Producto (grande)
        FUENTE_GRANDE + producto + FUENTE_NORMAL + "\n\n" +

        LINEA + "\n\n" +

        # Mensaje final
        "Gracias por su compra\n\n" +

        # Espacio para corte
        "\n\n\n"
    )

    return ticket
