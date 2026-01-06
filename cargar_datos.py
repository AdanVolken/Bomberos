"""
Script para cargar datos de empresa y productos en la base de datos
"""

from database import insert_empresa, insert_product, get_empresa, get_all_products

def cargar_empresa():
    """Carga o actualiza la información de la empresa"""
    print("\n" + "="*50)
    print("CARGAR INFORMACIÓN DE LA EMPRESA")
    print("="*50 + "\n")
    
    # Verificar si ya existe una empresa
    empresa_actual = get_empresa()
    if empresa_actual:
        print(f"Empresa actual: {empresa_actual['nombre']}")
        respuesta = input("¿Deseas actualizar la información? (s/n): ").lower()
        if respuesta not in ['s', 'si', 'y', 'yes']:
            return
    
    nombre = input("Nombre de la empresa: ").strip()
    if not nombre:
        print("El nombre no puede estar vacío.")
        return
    
    logo = input("Ruta de la imagen/logo (opcional, presiona Enter para omitir): ").strip()
    if not logo:
        logo = None
    
    insert_empresa(nombre, logo)
    print(f"\n[OK] Empresa '{nombre}' guardada correctamente\n")

def cargar_producto():
    """Carga un nuevo producto"""
    print("\n" + "="*50)
    print("CARGAR NUEVO PRODUCTO")
    print("="*50 + "\n")
    
    nombre = input("Nombre del producto: ").strip()
    if not nombre:
        print("El nombre no puede estar vacío.")
        return
    
    try:
        precio = float(input("Precio: ").strip())
        if precio < 0:
            print("El precio no puede ser negativo.")
            return
    except ValueError:
        print("El precio debe ser un número válido.")
        return
    
    imagen = input("Ruta de la imagen (opcional, presiona Enter para omitir): ").strip()
    if not imagen:
        imagen = None
    
    product_id = insert_product(nombre, precio, imagen)
    print(f"\n[OK] Producto '{nombre}' agregado con ID: {product_id}\n")

def listar_productos():
    """Lista todos los productos"""
    print("\n" + "="*50)
    print("PRODUCTOS EN LA BASE DE DATOS")
    print("="*50 + "\n")
    
    products = get_all_products()
    
    if not products:
        print("No hay productos en la base de datos.\n")
        return
    
    for i, product in enumerate(products, 1):
        print(f"{i}. {product['name']}")
        print(f"   Precio: ${product['price']}")
        print(f"   Imagen: {product.get('image', 'Sin imagen')}")
        print()

def menu_principal():
    """Menú principal para cargar datos"""
    while True:
        print("\n" + "="*50)
        print("SISTEMA DE TICKETS - CARGA DE DATOS")
        print("="*50)
        print("1. Cargar/Actualizar información de la empresa")
        print("2. Agregar nuevo producto")
        print("3. Listar productos existentes")
        print("4. Salir")
        print("="*50)
        
        opcion = input("\nSelecciona una opción (1-4): ").strip()
        
        if opcion == "1":
            cargar_empresa()
        elif opcion == "2":
            cargar_producto()
        elif opcion == "3":
            listar_productos()
        elif opcion == "4":
            print("\n¡Hasta luego!\n")
            break
        else:
            print("\nOpción no válida. Por favor selecciona 1-4.\n")

if __name__ == "__main__":
    menu_principal()

