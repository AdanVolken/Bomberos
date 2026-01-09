from escpos.printer import Usb

def imprimir_ticket(texto):
    """
    Imprime un ticket en impresora térmica USB
    """
    try:
        # 🔴 ESTOS VALORES DEPENDEN DE TU IMPRESORA
        # Los cambiamos después de probar
        p = Usb(0x04b8, 0x0202)  # ejemplo Epson

        p.set(align='center', bold=True)
        p.text(texto)
        p.cut()

        return True, "Ticket impreso correctamente"

    except Exception as e:
        return False, f"Error al imprimir: {e}"
