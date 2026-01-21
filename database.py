import sqlite3
import os
import sys
from typing import List, Dict, Optional, Tuple
from datetime import datetime

def resource_path(relative_path: str) -> str:
    """
    Obtiene la ruta correcta tanto en desarrollo como en PyInstaller
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

DB_NAME = resource_path("Sistema_Tickets_DB.db")

def get_connection():
    """Crea y retorna una conexión a la base de datos SQLite"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Inicializa la base de datos creando todas las tablas"""
    sql_file = resource_path("create_tables.sql")

    if not os.path.exists(sql_file):
        print(f"Error: No se encontró el archivo {sql_file}")
        return False

    conn = get_connection()
    cursor = conn.cursor()

    try:
        with open(sql_file, "r", encoding="utf-8", errors="ignore") as f:
            sql_script = f.read()

        cursor.executescript(sql_script)
        conn.commit()
        print("[OK] Base de datos inicializada correctamente")
        return True
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# ==================== EMPRESA ====================

def get_empresa() -> Optional[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, nombre_caja, logo FROM empresa LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "nombre": row["nombre"],
            "nombre_caja": row["nombre_caja"] if "nombre_caja" in row.keys() else None,
            "logo": row["logo"] if row["logo"] else None
        }
    return None

def insert_empresa(nombre: str, nombre_caja: str, logo: Optional[str] = None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT nombre FROM empresa LIMIT 1")
    exists = cursor.fetchone()

    if exists:
        cursor.execute(
            "UPDATE empresa SET nombre = ?, nombre_caja = ?, logo = ?",
            (nombre, nombre_caja, logo)
        )
    else:
        cursor.execute(
            "INSERT INTO empresa (nombre, nombre_caja, logo) VALUES (?, ?, ?)",
            (nombre, nombre_caja, logo)
        )

    conn.commit()
    conn.close()

# ==================== PRODUCTOS ====================

def insert_product(nombre: str, precio: float, imagen: Optional[str] = None, cantidad_disponible: int = 0):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO productos (nombre, precio, imagen, cantidad_vendida, cantidad_disponible)
        VALUES (?, ?, ?, 0, ?)
    """, (nombre, precio, imagen, cantidad_disponible))

    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    return product_id

def get_all_products() -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nombre, precio, imagen, cantidad_vendida, cantidad_disponible
        FROM productos
        ORDER BY nombre
    """)

    rows = cursor.fetchall()
    conn.close()

    products = []
    for row in rows:
        vendida = row["cantidad_vendida"] or 0
        disponible = row["cantidad_disponible"] or 0

        products.append({
            "id": row["id"],
            "name": row["nombre"],
            "price": row["precio"],
            "image": row["imagen"],
            "cantidad_vendida": vendida,
            "cantidad_disponible": disponible,
            "cantidad_restante": max(0, disponible)
        })

    return products

def get_product_by_id(product_id: int) -> Optional[Dict]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nombre, precio, imagen, cantidad_vendida, cantidad_disponible
        FROM productos WHERE id = ?
    """, (product_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    vendida = row["cantidad_vendida"] or 0
    disponible = row["cantidad_disponible"] or 0

    return {
        "id": row["id"],
        "name": row["nombre"],
        "price": row["precio"],
        "image": row["imagen"],
        "cantidad_vendida": vendida,
        "cantidad_disponible": disponible,
        "cantidad_restante": max(0, disponible)
    }

def update_product(product_id: int, nombre=None, precio=None, imagen=None, cantidad_disponible=None):
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
    if cantidad_disponible is not None:
        updates.append("cantidad_disponible = ?")
        values.append(cantidad_disponible)

    if updates:
        values.append(product_id)
        cursor.execute(
            f"UPDATE productos SET {', '.join(updates)} WHERE id = ?",
            values
        )
        conn.commit()

    conn.close()

def delete_product(product_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()

def registrar_venta(producto_id: int, cantidad: int) -> Tuple[bool, str]:
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT cantidad_disponible FROM productos WHERE id = ?", (producto_id,))
        row = cursor.fetchone()

        if not row:
            return False, "Producto no encontrado"

        stock = row["cantidad_disponible"] or 0
        if cantidad > stock:
            return False, f"Stock insuficiente. Disponible: {stock}"

        cursor.execute("""
            UPDATE productos
            SET cantidad_vendida = cantidad_vendida + ?,
                cantidad_disponible = cantidad_disponible - ?
            WHERE id = ?
        """, (cantidad, cantidad, producto_id))

        conn.commit()
        return True, "Venta registrada"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

# ==================== RESUMEN ====================

def get_ventas_summary() -> List[Dict]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nombre, precio, cantidad_vendida, cantidad_disponible,
               (precio * cantidad_vendida) AS ingresos_totales
        FROM productos
        ORDER BY cantidad_vendida DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [{
        "producto_id": r["id"],
        "nombre": r["nombre"],
        "precio": r["precio"],
        "unidades_vendidas": r["cantidad_vendida"] or 0,
        "stock_actual": r["cantidad_disponible"] or 0,
        "ingresos_totales": r["ingresos_totales"] or 0
    } for r in rows]
