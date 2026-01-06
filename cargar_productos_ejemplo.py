"""
Script para cargar productos de ejemplo directamente sin interacción
"""

from database import init_database, insert_empresa, insert_product
import os

def cargar_datos_ejemplo():
    """Carga datos de ejemplo en la base de datos"""
    
    # Asegurar que la base de datos esté inicializada
    if not os.path.exists("Sistema_Tickets_DB.db"):
        print("Inicializando base de datos...")
        init_database()
    
    print("\n" + "="*50)
    print("CARGANDO DATOS DE EJEMPLO")
    print("="*50 + "\n")
    
    # Cargar empresa
    print("1. Cargando información de la empresa...")
    insert_empresa(
        nombre="Mi Restaurante Rápido",
        logo="images/logo.jpg"
    )
    print("   [OK] Empresa configurada\n")
    
    # Productos de comida rápida
    productos = [
        {
            "nombre": "Hamburguesa Clásica",
            "precio": 3200,
            "imagen": "images/hamburguesa.jpg"
        },
        {
            "nombre": "Pizza Margarita",
            "precio": 2500,
            "imagen": "images/pizza.jpg"
        },
        {
            "nombre": "Papas Fritas",
            "precio": 1200,
            "imagen": "images/papas.jpg"
        },
        {
            "nombre": "Hot Dog",
            "precio": 1800,
            "imagen": "images/hotdog.jpg"
        },
        {
            "nombre": "Tacos",
            "precio": 2000,
            "imagen": "images/tacos.jpg"
        },
        {
            "nombre": "Burritos",
            "precio": 2200,
            "imagen": "images/burritos.jpg"
        },
        {
            "nombre": "Alitas de Pollo",
            "precio": 2800,
            "imagen": "images/alitas.jpg"
        },
        {
            "nombre": "Nachos",
            "precio": 1500,
            "imagen": "images/nachos.jpg"
        },
    ]
    
    print("2. Cargando productos...")
    for producto in productos:
        insert_product(
            nombre=producto["nombre"],
            precio=producto["precio"],
            imagen=producto["imagen"]
        )
        print(f"   [OK] {producto['nombre']} agregado")
    
    print("\n" + "="*50)
    print("DATOS CARGADOS EXITOSAMENTE!")
    print("="*50)
    print("\nAhora puedes ejecutar la aplicación con:")
    print("  python main.py\n")

if __name__ == "__main__":
    cargar_datos_ejemplo()

