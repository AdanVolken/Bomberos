# 📋 Guía para Cargar Datos en el Sistema de Tickets

## 🚀 Inicio Rápido

### 1. Inicializar la Base de Datos (Primera vez)

Ejecuta este comando **una sola vez** para crear las tablas:

```powershell
python SistemaTicket\init_db.py
```

Este script:
- ✅ Crea todas las tablas necesarias (empresa, productos, ventas)
- ✅ Te pregunta si quieres cargar datos de ejemplo
- ✅ Si respondes "s", carga productos de comida rápida de ejemplo

---

## 📦 Cargar Datos

### Opción 1: Usar el Script Interactivo (Recomendado)

Ejecuta el script de carga de datos:

```powershell
python SistemaTicket\cargar_datos.py
```

Este script te permite:
- **Cargar/Actualizar información de la empresa** (nombre e imagen/logo)
- **Agregar nuevos productos** (nombre, descripción, precio, imagen)
- **Listar productos existentes**

### Opción 2: Usar Python Directamente

Puedes cargar datos directamente desde Python:

```python
from database import insert_empresa, insert_product

# Cargar empresa
insert_empresa(
    nombre="Mi Restaurante Rápido",
    imagen="images/logo.jpg"  # Opcional
)

# Cargar productos
insert_product(
    nombre="Hamburguesa Clásica",
    descripcion="Hamburguesa con carne, lechuga, tomate y queso",
    precio=3200,
    imagen="images/hamburguesa.jpg"  # Opcional
)
```

---

## 🖼️ Sobre las Imágenes

### Estructura de Carpetas Recomendada

```
SistemaTicket/
├── images/
│   ├── logo.jpg          (Logo de la empresa)
│   ├── hamburguesa.jpg   (Imagen del producto)
│   ├── pizza.jpg
│   └── ...
```

### Rutas de Imágenes

- Puedes usar rutas relativas: `"images/hamburguesa.jpg"`
- O rutas absolutas: `"C:/Users/PC/Documents/Sistema_Tickets/SistemaTicket/images/hamburguesa.jpg"`
- Si no proporcionas imagen, el sistema usará un fondo de color por defecto

---

## 📊 Estructura de la Base de Datos

### Tabla: `empresa`
- `id` - ID único
- `nombre` - Nombre de la empresa
- `imagen` - Ruta del logo (opcional)

### Tabla: `productos`
- `id` - ID único
- `nombre` - Nombre del producto
- `descripcion` - Descripción del producto
- `precio` - Precio (número decimal)
- `imagen` - Ruta de la imagen (opcional)
- `activo` - Si está activo (1) o inactivo (0)

### Tabla: `ventas`
- `id` - ID único
- `producto_id` - ID del producto vendido
- `cantidad` - Cantidad vendida
- `precio_unitario` - Precio al momento de la venta
- `total` - Total de la venta (cantidad × precio_unitario)
- `fecha_venta` - Fecha y hora de la venta

---

## 🔍 Consultar Datos

### Ver Resumen de Ventas

```python
from database import get_ventas_summary

resumen = get_ventas_summary()
for item in resumen:
    print(f"{item['nombre']}: {item['unidades_vendidas']} unidades vendidas")
```

### Ver Ventas de un Producto

```python
from database import get_ventas_by_product

ventas = get_ventas_by_product(producto_id=1)
for venta in ventas:
    print(f"Cantidad: {venta['cantidad']}, Total: ${venta['total']}")
```

---

## ⚠️ Notas Importantes

1. **Primera ejecución**: Siempre ejecuta `init_db.py` primero para crear las tablas
2. **Imágenes**: Las imágenes son opcionales, pero mejoran la experiencia visual
3. **Precios**: Los precios se guardan como números decimales (REAL en SQLite)
4. **Ventas**: Las ventas se registran automáticamente cuando presionas "Imprimir ticket" en la aplicación

---

## 🆘 Solución de Problemas

### Error: "No se encuentra la base de datos"
- Ejecuta `init_db.py` primero

### Error: "No hay productos en la base de datos"
- Ejecuta `init_db.py` y responde "s" para cargar datos de ejemplo
- O usa `cargar_datos.py` para agregar productos manualmente

### Las imágenes no se muestran
- Verifica que las rutas de las imágenes sean correctas
- Asegúrate de que los archivos de imagen existan en la ubicación especificada

