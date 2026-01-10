from datetime import datetime

# Definición de comandos ESC/POS
# GS ! n (Tamaño de fuente: 0x11 es doble alto y doble ancho)
FUENTE_GRANDE = "\x1d\x21\x11" 
# ESC E 1 (Activar negrita)
NEGRITA_ON = "\x1b\x45\x01"
# ESC E 0 (Desactivar negrita y volver a fuente normal)
NORMAL = "\x1b\x45\x00\x1d\x21\x00"
# ESC a 1 (Centrar texto)
CENTRO = "\x1b\x61\x01"

def crear_tickets(productos, empresa):
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
    print("Vamos Picante - Aplicando Formato Grande")
    
    # Armamos el ticket con los comandos incrustados
    # Nota: Los comandos deben ir antes del texto que queremos afectar
    lineas = [
        CENTRO,              # Centrar todo el ticket
        NEGRITA_ON + empresa + NEGRITA_ON,
        "-" * 24,
        # Aquí el producto va en tamaño DOBLE (0x11)
        FUENTE_GRANDE + producto + NORMAL, 
        "-" * 24,
        "Gracias por su compra!",
        "-" * 24,
        "\n"
    ]
    return "".join(lineas)