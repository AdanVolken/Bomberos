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


def generar_texto_ticket(empresa, producto):
    print("Vamos Picante")
    lineas = [
        empresa,
        "-" * 24,
        producto
    ]
    return "\n".join(lineas)
