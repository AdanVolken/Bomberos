from datetime import datetime


def crear_tickets(productos, empresa):
    """
    productos: lista de productos (cart)
    empresa: dict con al menos { nombre }

    Devuelve una lista de tickets (uno por producto)
    """

    tickets = []

    for producto in productos:
        ticket = {
            "empresa": empresa.get("nombre", "Sistema de Tickets"),
            "producto": producto["name"],
            "precio": producto["price"],
            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
        tickets.append(ticket)

    return tickets


def generar_texto_ticket(ticket):
    """
    Genera el texto de UN ticket (80mm aprox)
    """

    lineas = [
        ticket["empresa"],
        "-" * 24,
        ticket["producto"],
        f"${int(ticket['precio'])}",
        "-" * 24,
        ticket["fecha"]
    ]

    return "\n".join(lineas)
