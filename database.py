import sqlite3
import os
import sys
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import shutil
import uuid
import hashlib
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



def get_app_data_dir():
    base = os.getenv("APPDATA") or os.path.expanduser("~")
    path = os.path.join(base, "MiniPOS")
    os.makedirs(path, exist_ok=True)
    return path

def get_db_path():
    app_dir = get_app_data_dir()
    db_path = os.path.join(app_dir, "Sistema_Tickets_DB.db")

    if not os.path.exists(db_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        original_db = os.path.join(base_path, "Sistema_Tickets_DB.db")

        if os.path.exists(original_db):
            shutil.copyfile(original_db, db_path)
        else:
            # Caso DEV: crear DB vacía
            conn = sqlite3.connect(db_path)
            conn.close()

    return db_path


DB_NAME = get_db_path()

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

# ==================== MIGRACIONES ====================

def crear_tablas_si_no_existen():
    """Crea todas las tablas necesarias si no existen"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # ==================== EMPRESA ====================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS empresa (
                nombre TEXT NOT NULL,
                nombre_caja TEXT,
                logo TEXT
            )
        """)

        # Verificar si la columna nombre_caja existe en empresa
        cursor.execute("PRAGMA table_info(empresa)")
        columns = [column[1] for column in cursor.fetchall()]
        if "nombre_caja" not in columns:
            cursor.execute("ALTER TABLE empresa ADD COLUMN nombre_caja TEXT")

        # ==================== PRODUCTOS ====================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                precio REAL NOT NULL,
                imagen TEXT,
                cantidad_vendida INTEGER DEFAULT 0,
                cantidad_disponible INTEGER DEFAULT 0
            )
        """)

        # ==================== LICENCIAS ====================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS licencia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                max_maquinas INTEGER NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS licencia_maquinas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                licencia_id INTEGER NOT NULL,
                mac TEXT NOT NULL,
                fecha_activacion TEXT NOT NULL,
                FOREIGN KEY (licencia_id) REFERENCES licencia(id)
            )
        """)

        # ==================== MEDIOS DE PAGO ====================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medios_pago (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                activo INTEGER DEFAULT 1
            )
        """)

        # Insertar medio de pago por defecto si no existe
        cursor.execute("""
            INSERT OR IGNORE INTO medios_pago (id, nombre, activo)
            VALUES (1, 'Efectivo', 1)
        """)

        # ==================== CORTES DE CAJA (antes que ventas por FK) ====================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cortes_caja (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora TEXT NOT NULL,
                total_acumulado REAL NOT NULL,
                ultima_venta_id INTEGER NOT NULL
            )
        """)

        # ==================== VENTAS ====================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora TEXT NOT NULL,
                total REAL NOT NULL,
                medio_pago_id INTEGER NOT NULL,
                corte_id INTEGER,
                FOREIGN KEY (medio_pago_id) REFERENCES medios_pago(id),
                FOREIGN KEY (corte_id) REFERENCES cortes_caja(id)
            )
        """)

        # ==================== DETALLE DE VENTAS ====================
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas_detalle (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id INTEGER NOT NULL,
                producto_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                FOREIGN KEY (venta_id) REFERENCES ventas(id),
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            )
        """)

        conn.commit()

    except Exception as e:
        print(f"[ERROR] Error al crear tablas: {e}")
        conn.rollback()
    finally:
        conn.close()


# Ejecutar creación de tablas al importar el módulo
crear_tablas_si_no_existen()

# ==================== EMPRESA ====================

def get_empresa() -> Optional[Dict]:
    conn = get_connection()
    cursor = conn.cursor()
    
    # Intentar obtener todas las columnas disponibles
    try:
        cursor.execute("SELECT * FROM empresa LIMIT 1")
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "nombre": row["nombre"] if "nombre" in row.keys() else None,
                "nombre_caja": row["nombre_caja"] if "nombre_caja" in row.keys() else None,
                "logo": row["logo"] if "logo" in row.keys() else None
            }
    except Exception as e:
        # Si falla, intentar solo con nombre y logo
        try:
            cursor.execute("SELECT nombre, logo FROM empresa LIMIT 1")
            row = cursor.fetchone()
            conn.close()
            if row:
                return {
                    "nombre": row["nombre"],
                    "nombre_caja": None,
                    "logo": row["logo"] if "logo" in row.keys() else None
                }
        except:
            pass
        conn.close()
    
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


# ==================== LICENCIA ====================

def crear_licencia(cliente: str, password: str, max_maquinas: int):
    conn = get_connection()
    cursor = conn.cursor()

    password_hash = hashlib.sha256(password.encode()).hexdigest()

    cursor.execute("""
        INSERT INTO licencia (cliente, password_hash, max_maquinas)
        VALUES (?, ?, ?)
    """, (cliente, password_hash, max_maquinas))

    conn.commit()
    conn.close()

def validar_licencia(cliente: str, password: str):
    conn = get_connection()
    cursor = conn.cursor()

    password_hash = hashlib.sha256(password.encode()).hexdigest()

    cursor.execute("""
        SELECT id, max_maquinas FROM licencia
        WHERE cliente = ? AND password_hash = ?
    """, (cliente, password_hash))

    licencia = cursor.fetchone()

    if not licencia:
        conn.close()
        return False, "Usuario o contraseña incorrectos"

    licencia_id = licencia["id"]
    max_maquinas = licencia["max_maquinas"]

    mac_actual = get_mac_address()

    # Ver si ya está registrada esta MAC
    cursor.execute("""
        SELECT id FROM licencia_maquinas
        WHERE licencia_id = ? AND mac = ?
    """, (licencia_id, mac_actual))

    existe = cursor.fetchone()

    if existe:
        conn.close()
        return True, "Licencia válida"

    # Contar máquinas actuales
    cursor.execute("""
        SELECT COUNT(*) as total FROM licencia_maquinas
        WHERE licencia_id = ?
    """, (licencia_id,))

    total_maquinas = cursor.fetchone()["total"]

    if total_maquinas >= max_maquinas:
        conn.close()
        return False, "Se alcanzó el límite de máquinas permitidas"

    # Registrar nueva máquina
    cursor.execute("""
        INSERT INTO licencia_maquinas (licencia_id, mac, fecha_activacion)
        VALUES (?, ?, ?)
    """, (licencia_id, mac_actual, datetime.now().isoformat()))

    conn.commit()
    conn.close()

    return True, "Máquina registrada correctamente"


def obtener_maquinas_licencia(licencia_id: int):
    """Obtiene todas las máquinas registradas para una licencia"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, mac, fecha_activacion 
        FROM licencia_maquinas
        WHERE licencia_id = ?
        ORDER BY fecha_activacion DESC
    """, (licencia_id,))
    
    maquinas = cursor.fetchall()
    conn.close()
    
    return [{
        "id": m["id"],
        "mac": m["mac"],
        "fecha_activacion": m["fecha_activacion"]
    } for m in maquinas]

def eliminar_maquina_licencia(maquina_id: int):
    """Elimina una máquina registrada de una licencia"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM licencia_maquinas WHERE id = ?", (maquina_id,))
    
    conn.commit()
    conn.close()
    
    return True

# ==================== UTILIDADES ====================
def get_mac_address():
    return ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                     for ele in range(0, 8*6, 8)][::-1])

# ===================== MEDIOS DE PAGO ====================
def get_medios_pago(activos_only: bool = True):
    conn = get_connection()
    cursor = conn.cursor()

    if activos_only:
        cursor.execute("""
            SELECT id, nombre FROM medios_pago
            WHERE activo = 1
            ORDER BY nombre
        """)
    else:
        cursor.execute("""
            SELECT id, nombre, activo FROM medios_pago
            ORDER BY nombre
        """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# ===================== VENTAS ====================
def insert_medio_pago(nombre: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO medios_pago (nombre, activo)
        VALUES (?, 1)
    """, (nombre,))

    conn.commit()
    conn.close()


def toggle_medio_pago(medio_id: int, activo: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE medios_pago
        SET activo = ?
        WHERE id = ?
    """, (activo, medio_id))

    conn.commit()
    conn.close()



# ==================== VENTAS REALES ====================
def crear_venta(total: float, medio_pago_id: int) -> int:
    conn = get_connection()
    cursor = conn.cursor()

    fecha_hora = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO ventas (fecha_hora, total, medio_pago_id)
        VALUES (?, ?, ?)
    """, (fecha_hora, total, medio_pago_id))

    venta_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return venta_id

# ===================== DETALLE DE VENTAS =====================
def insertar_detalle_venta(venta_id: int, producto_id: int, cantidad: int, precio_unitario: float):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO ventas_detalle (venta_id, producto_id, cantidad, precio_unitario)
        VALUES (?, ?, ?, ?)
    """, (venta_id, producto_id, cantidad, precio_unitario))

    conn.commit()
    conn.close()

# ==================== RESUMEN POR MEDIO DE PAGO ====================
def resumen_por_medio_pago():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT m.nombre, SUM(v.total) as total
        FROM ventas v
        JOIN medios_pago m ON v.medio_pago_id = m.id
        GROUP BY m.nombre
        ORDER BY total DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

# ==================== CORTE DE CAJA ====================

def obtener_ultimo_corte():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, fecha_hora
        FROM cortes_caja
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def crear_corte_caja(total_acumulado: float, ultima_venta_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    fecha_hora = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO cortes_caja (fecha_hora, total_acumulado, ultima_venta_id)
        VALUES (?, ?, ?)
    """, (fecha_hora, total_acumulado, ultima_venta_id))

    corte_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return corte_id

def obtener_ultima_venta_id():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM ventas
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    return row["id"] if row else 0



def ventas_desde_ultimo_corte():
    conn = get_connection()
    cursor = conn.cursor()

    ultimo_corte = obtener_ultimo_corte()

    if ultimo_corte:
        cursor.execute("""
            SELECT * FROM ventas
            WHERE id > ?
        """, (ultimo_corte["ultima_venta_id"],))
    else:
        cursor.execute("SELECT * FROM ventas")

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]
