"""
Script para inicializar la base de datos del Sistema de Tickets
Ejecuta este script una vez para crear todas las tablas necesarias
"""

from database import init_database, insert_empresa, insert_product

def populate_initial_data():
    """Pobla la base de datos con datos iniciales de ejemplo"""
    
    print("\n" + "="*50)
    print("POBLANDO BASE DE DATOS CON DATOS INICIALES")
    print("="*50 + "\n")
    
    # Insertar información de la empresa
    print("1. Insertando información de la empresa...")
    insert_empresa(
        nombre="Mi Restaurante Rápido",
        imagen="images/logo.jpg"
    )
    print("   [OK] Empresa configurada\n")
    
    # Productos de comida rápida con sus imágenes
    productos_iniciales = [
        {
            "nombre": "Hamburguesa Clásica",
            "descripcion": "Hamburguesa con carne, lechuga, tomate y queso",
            "precio": 3200,
            "imagen": "images/hamburguesa.jpg"
        },
        {
            "nombre": "Pizza Margarita",
            "descripcion": "Pizza con queso mozzarella y tomate",
            "precio": 2500,
            "imagen": "images/pizza.jpg"
        },
        {
            "nombre": "Papas Fritas",
            "descripcion": "Porción de papas fritas crujientes",
            "precio": 1200,
            "imagen": "images/papas.jpg"
        },
        {
            "nombre": "Hot Dog",
            "descripcion": "Hot dog con salchicha y aderezos",
            "precio": 1800,
            "imagen": "images/hotdog.jpg"
        },
        {
            "nombre": "Tacos",
            "descripcion": "Tacos de carne con salsa y vegetales",
            "precio": 2000,
            "imagen": "images/tacos.jpg"
        },
        {
            "nombre": "Burritos",
            "descripcion": "Burrito grande con carne y frijoles",
            "precio": 2200,
            "imagen": "images/burritos.jpg"
        },
        {
            "nombre": "Alitas de Pollo",
            "descripcion": "6 alitas de pollo con salsa picante",
            "precio": 2800,
            "imagen": "images/alitas.jpg"
        },
        {
            "nombre": "Nachos",
            "descripcion": "Nachos con queso derretido y jalapeños",
            "precio": 1500,
            "imagen": "images/nachos.jpg"
        },
    ]
    
    print("2. Insertando productos iniciales...")
    for producto in productos_iniciales:
        insert_product(
            nombre=producto["nombre"],
            descripcion=producto["descripcion"],
            precio=producto["precio"],
            imagen=producto["imagen"]
        )
        print(f"   [OK] {producto['nombre']} agregado")
    
    print("\n" + "="*50)
    print("¡BASE DE DATOS INICIALIZADA EXITOSAMENTE!")
    print("="*50 + "\n")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("INICIALIZANDO BASE DE DATOS")
    print("="*50 + "\n")
    
    # Crear las tablas
    if init_database():
        # Preguntar si quiere poblar con datos iniciales
        respuesta = input("¿Deseas poblar la base de datos con datos de ejemplo? (s/n): ").lower()
        if respuesta == 's' or respuesta == 'si' or respuesta == 'y' or respuesta == 'yes':
            populate_initial_data()
        else:
            print("\nBase de datos creada. Puedes agregar datos manualmente.\n")
    else:
        print("\nError al inicializar la base de datos.\n")

