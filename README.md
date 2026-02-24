# Mini POS — Sistema de Punto de Venta

Sistema de punto de venta (POS) desarrollado en Python con interfaz gráfica en Flet. Incluye autenticación offline, control de licencias por máquina, ventas, impresión de tickets, cortes de caja y dashboard de ventas.

---

## Características

- **Inicio de sesión obligatorio**: acceso con usuario/contraseña antes de usar el POS.
- **Usuario administrador**: usuario `admin` con contraseña `daleboca` (acceso directo, sin validar licencia ni MAC).
- **Licencias por cliente**: para el resto de usuarios, validación contra la tabla `licencia` con hash SHA256 de la contraseña.
- **Control por máquina**: límite de máquinas por licencia (`max_maquinas`); registro de dirección MAC en `licencia_maquinas`; bloqueo si se supera el cupo.
- **Gestión de productos**: alta, edición, eliminación y listado de productos con precios y stock.
- **Ventas**: carrito, impresión de ticket por producto y registro en base de datos.
- **Empresa y caja**: configuración de nombre de empresa y nombre de caja (obligatorio al inicio).
- **Medios de pago**: configuración de medios de pago para las ventas.
- **Cortes de caja**: realización de cortes y asociación de ventas al corte.
- **Dashboard de ventas**: total vendido, unidades, cantidad de ventas, promedio; filtros por producto, medio de pago y corte; exportar Excel, imprimir resumen y generar PDF.
- **Administración de cuentas** (solo admin): ver licencias, modificar `max_maquinas`, cambiar contraseñas y eliminar MACs para liberar cupos.

Todo el sistema funciona **offline** usando una base de datos SQLite.

---

## Tecnologías

- **Python 3**
- **Flet** (interfaz gráfica)
- **SQLite** (base de datos)
- **PyInstaller** (generación del ejecutable)
- **ReportLab** (PDF), **pandas** / **openpyxl** (Excel), **python-escpos** (impresión térmica)

---

## Requisitos

- Python 3.10 o superior (recomendado 3.11+)
- Dependencias listadas en `requirements.txt`

---

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/TU_USUARIO/SistemaTicket.git
   cd SistemaTicket
   ```

2. Crear un entorno virtual (recomendado):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Asegurarse de tener en la raíz del proyecto:
   - `main.py`
   - `create_tables.sql`
   - `Sistema_Tickets_DB.db` (opcional; si no existe, la aplicación crea las tablas al iniciar)
   - `ticketIcono.ico` (opcional; para el icono de la ventana y del .exe)

---

## Ejecución

Desde la raíz del proyecto:

```bash
python main.py
```

La base de datos se guarda en:

- **Windows**: `%APPDATA%\MiniPOS\Sistema_Tickets_DB.db`
- Si no existe, se crean las tablas automáticamente al importar el módulo `database`.

---

## Generar el ejecutable (.exe)

Para crear un ejecutable portable con PyInstaller (Windows):

```bash
pyinstaller --onefile --windowed --name MiniPOS --icon=ticketIcono.ico --add-data "Sistema_Tickets_DB.db;." --add-data "create_tables.sql;." main.py
```

- `--onefile`: un solo .exe.
- `--windowed`: sin consola.
- `--name MiniPOS`: nombre del ejecutable.
- `--icon=ticketIcono.ico`: icono de la aplicación (debe existir en la raíz).
- `--add-data`: incluye la base de datos y el SQL en el ejecutable (en Windows se usa `;` como separador).

El .exe se genera en `dist/MiniPOS.exe`. La primera vez que se ejecute, creará/usa la base de datos en `%APPDATA%\MiniPOS\`.

**En Linux/macOS** el separador de `--add-data` es `:`:
```bash
pyinstaller --onefile --windowed --name MiniPOS --icon=ticketIcono.ico --add-data "Sistema_Tickets_DB.db:." --add-data "create_tables.sql:." main.py
```

---

## Descargas

En la siguiente carpeta de Google Drive están disponibles el **ejecutable** de Mini POS y el **instalador de los drivers** para las impresoras térmicas:

**[📁 Mini POS — Ejecutable y drivers de impresoras](https://drive.google.com/drive/folders/1OHRksN_aXonEG_mwtj2adKUWr0MGXkAo)**

- Descargar e instalar los drivers antes de usar la impresión de tickets.
- El .exe puede ejecutarse sin instalar Python en el equipo.

---

## Estructura del proyecto (principales archivos)

| Archivo / carpeta        | Descripción |
|--------------------------|-------------|
| `main.py`                | Punto de entrada: login y pantalla principal del POS. |
| `inicio_sesion.py`       | Popup de inicio de sesión (admin vs licencias). |
| `administracion_cuentas.py` | Panel de administración de licencias (solo admin). |
| `database.py`            | Conexión SQLite, creación de tablas y lógica de negocio (empresa, productos, ventas, licencias, cortes, etc.). |
| `ventas.py`              | Lógica de ventas y generación de texto de tickets. |
| `printer.py`             | Envío a impresora térmica (tickets). |
| `dashboard.py`           | Dashboard de ventas con filtros y exportación. |
| `popupEmpresa.py`        | Configuración de empresa y caja. |
| `products_crud_dialog.py`| Diálogo de administración de productos. |
| `corte_caja.py`          | Lógica de corte de caja. |
| `admin_medios_pago.py`   | Administración de medios de pago. |
| `generarExcel.py`        | Exportación de ventas a Excel. |
| `generar_pdf_ventas.py`  | Generación de PDF de resumen de ventas. |
| `generar_ticket_ventas_totales` | Texto del ticket de resumen de ventas. |
| `create_tables.sql`      | Definición de tablas (referencia; la app crea tablas desde `database.py`). |
| `Sistema_Tickets_DB.db`  | Base SQLite (opcional en desarrollo; en producción puede generarse en `%APPDATA%\MiniPOS\`). |
| `requirements.txt`      | Dependencias Python. |

---

## Base de datos (SQLite)

Tablas principales:

- **empresa**: nombre, nombre_caja, logo.
- **productos**: id, nombre, precio, imagen, cantidad_vendida, cantidad_disponible.
- **licencia**: id, cliente, password_hash, max_maquinas.
- **licencia_maquinas**: licencia_id, mac, fecha_activacion.
- **medios_pago**: id, nombre, activo.
- **ventas**: id, fecha_hora, total, medio_pago_id, corte_id.
- **ventas_detalle**: venta_id, producto_id, cantidad, precio_unitario.
- **cortes_caja**: id, fecha_hora, total_acumulado, ultima_venta_id.

La aplicación crea y actualiza tablas automáticamente al iniciar (incluyendo migraciones básicas como la columna `nombre_caja` en `empresa`).

---

## Uso rápido

1. Ejecutar `python main.py` (o `dist/MiniPOS.exe` si usas el .exe).
2. Iniciar sesión:
   - **Admin**: usuario `admin`, contraseña `daleboca`.
   - **Otros**: usuario y contraseña de una licencia en la base de datos (se valida MAC y cupo de máquinas).
3. Si es la primera vez, completar empresa y nombre de caja en el popup.
4. Usar el POS: agregar productos al carrito, imprimir ticket y, si corresponde, realizar cortes de caja y consultar el dashboard de ventas.

---

## Licencia

Este proyecto es de uso libre según los términos que definas en tu repositorio.
