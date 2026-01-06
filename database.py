import sqlite3
import os
from typing import List, Dict, Optional
from datetime import datetime

DB_NAME = "Sistema_Tickets_DB.db"

def get_connection():
    """Crea y retorna una conexión a la base de datos SQLite"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Para acceder a las columnas por nombre
    return conn

def init_database():
    """Inicializa la base de datos creando todas las tablas"""
    # Leer el script SQL
    sql_file = os.path.join(os.path.dirname(__file__), "create_tables.sql")
    
    if not os.path.exists(sql_file):
        print(f"Error: No se encontró el archivo {sql_file}")
        return False
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Leer y ejecutar el script SQL
        with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
            sql_script = f.read()
        
        # Ejecutar el script completo
        cursor.executescript(sql_script)
        conn.commit()
        print("[OK] Base de datos inicializada correctamente")
        print("[OK] Tablas creadas: empresa, productos, ventas")
        return True
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# ==================== EMPRESA ====================

def get_empresa() -> Optional[Dict]:
    """Obtiene la información de la empresa"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT nombre, logo FROM empresa LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "nombre": row["nombre"],
            "logo": row["logo"] if row["logo"] else None
        }
    return None

def insert_empresa(nombre: str, logo: Optional[str] = None):
    """Inserta o actualiza la información de la empresa"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verificar si ya existe una empresa
    cursor.execute("SELECT nombre FROM empresa LIMIT 1")
    existing = cursor.fetchone()
    
    if existing:
        # Actualizar
        cursor.execute("""
            UPDATE empresa 
            SET nombre = ?, logo = ?
        """, (nombre, logo))
    else:
        # Insertar
        cursor.execute("""
            INSERT INTO empresa (nombre, logo)
            VALUES (?, ?)
        """, (nombre, logo))
    
    conn.commit()
    conn.close()

# ==================== PRODUCTOS ====================

def insert_product(nombre: str, precio: float, imagen: Optional[str] = None):
    """Inserta un nuevo producto en la base de datos"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO productos (nombre, precio, imagen, cantidad_vendida)
        VALUES (?, ?, ?, 0)
    """, (nombre, precio, imagen))
    
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    return product_id

def get_all_products() -> List[Dict]:
    """Obtiene todos los productos"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, nombre, precio, imagen, cantidad_vendida
        FROM productos
        ORDER BY nombre
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    products = []
    for row in rows:
        products.append({
            "id": row["id"],
            "name": row["nombre"],
            "price": row["precio"],
            "image": row["imagen"] if row["imagen"] else None,
            "cantidad_vendida": row["cantidad_vendida"]
        })
    
    return products

def get_product_by_id(product_id: int) -> Optional[Dict]:
    """Obtiene un producto por su ID"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, nombre, precio, imagen, cantidad_vendida
        FROM productos
        WHERE id = ?
    """, (product_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "id": row["id"],
            "name": row["nombre"],
            "price": row["precio"],
            "image": row["imagen"] if row["imagen"] else None,
            "cantidad_vendida": row["cantidad_vendida"]
        }
    return None

def update_product(product_id: int, nombre: str = None, precio: float = None, imagen: str = None):
    """Actualiza un producto"""
    conn = get_connection()
    cursor = conn.cursor()
    
    updates = []
    values = []
    
    if nombre is not None:
        updates.append("nombre = ?")
        values.append(nombre)
    if precio is not None:
        updates.append("precio = ?")
        values.append(precio)
    if imagen is not None:
        updates.append("imagen = ?")
        values.append(imagen)
    
    if updates:
        values.append(product_id)
        query = f"UPDATE productos SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
    
    conn.close()

def delete_product(product_id: int):
    """Elimina un producto"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM productos WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

def registrar_venta(producto_id: int, cantidad: int):
    """Registra una venta aumentando cantidad_vendida del producto"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE productos 
        SET cantidad_vendida = cantidad_vendida + ?
        WHERE id = ?
    """, (cantidad, producto_id))
    
    conn.commit()
    conn.close()

# ==================== VENTAS ====================

def get_ventas_summary() -> List[Dict]:
    """Obtiene un resumen de ventas por producto usando cantidad_vendida"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            id,
            nombre,
            precio,
            cantidad_vendida,
            (precio * cantidad_vendida) as ingresos_totales
        FROM productos
        ORDER BY cantidad_vendida DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    summary = []
    for row in rows:
        summary.append({
            "producto_id": row["id"],
            "nombre": row["nombre"],
            "precio": row["precio"],
            "unidades_vendidas": row["cantidad_vendida"] or 0,
            "ingresos_totales": row["ingresos_totales"] or 0.0
        })
    
    return summary

