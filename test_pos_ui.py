import pyautogui
import time
import random

# Seguridad: mover mouse a esquina para abortar
pyautogui.FAILSAFE = True

# Tiempo entre acciones
DELAY = 0.3

# Cantidad de iteraciones (ventas)
VENTAS = 20

# Coordenadas de productos (AJUSTAR si hace falta)
PRODUCTOS = [
    (571, 406),   # Producto 1
    (889, 391),   # Producto 2
    (1295, 377),  # Producto 3
]

# Botones
BOTON_IMPRIMIR = (1612, 975)
BOTON_ELIMINAR = (1825, 139)

print(" Arranca en 5 segundos...")
time.sleep(5)

for venta in range(VENTAS):
    print(f" Venta #{venta + 1}")

    # Cantidad de productos en esta venta
    clicks = random.randint(1, 10)

    for _ in range(clicks):
        x, y = random.choice(PRODUCTOS)
        pyautogui.click(x, y)
        time.sleep(DELAY)

        # 30% de probabilidad de eliminar un producto
        if random.random() < 0.3:
            time.sleep(DELAY)
            pyautogui.click(*BOTON_ELIMINAR)
            time.sleep(DELAY)

    time.sleep(1)

    # Imprimir ticket
    pyautogui.click(*BOTON_IMPRIMIR)
    time.sleep(2)

print(" Testing finalizado")
