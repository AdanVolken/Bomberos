import win32print

def imprimir_ticket(texto):
    print("Iniciando impresión directa (Sin librerías intermedias)...")
    
    # Nombre exacto que vimos en tu consola
    nombre_impresora = "POS-58" 
    
    try:
        # 1. Abrir la impresora
        hPrinter = win32print.OpenPrinter(nombre_impresora)
        
        try:
            # 2. Configurar el documento en modo RAW (binario puro)
            # Esto evita que Windows intente usar drivers de texto y permite enviar el comando de CORTE
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("Ticket ", None, "RAW"))
            win32print.StartPagePrinter(hPrinter)
            
            # 3. Preparar los datos
            # \x1d\x56\x00 es el comando ESC/POS para CORTAR papel
            # Añadimos saltos de línea (\n) para que el texto pase la cuchilla
            corte_comando = b"\x1d\x56\x00"
            contenido_final = (texto + "\n\n\n\n").encode('latin-1') + corte_comando
            
            # 4. Enviar bytes
            win32print.WritePrinter(hPrinter, contenido_final)
            
            win32print.EndPagePrinter(hPrinter)
            win32print.EndDocPrinter(hPrinter)
            
            print("¡Éxito! El ticket debería estar saliendo.")
            return True, "Ticket enviado"
            
        finally:
            win32print.ClosePrinter(hPrinter)
            
    except Exception as e:
        error_detallado = f"Error crítico de hardware: {str(e)}"
        print(error_detallado)
        return False, error_detallado