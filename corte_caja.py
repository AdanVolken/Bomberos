from database import (
    ventas_desde_ultimo_corte,
    crear_corte_caja,
    obtener_ultima_venta_id,
    resumen_por_medio_pago,
    get_empresa
)
from generar_ticket_corte import generar_ticket_corte
from printer import imprimir_ticket


def realizar_corte():

    ventas = ventas_desde_ultimo_corte()

    if not ventas:
        return False, "No hay ventas desde el último corte"

    resumen = resumen_por_medio_pago()

    total_general = sum(v["total"] for v in resumen if v["total"])

    empresa = get_empresa()
    nombre_empresa = empresa["nombre"] if empresa else "Mini POS"

    texto_ticket = generar_ticket_corte(
        empresa_nombre=nombre_empresa,
        resumen_medios=resumen,
        total_general=total_general
    )

    ok, msg = imprimir_ticket(texto_ticket)

    if not ok:
        return False, msg

    # 🔹 NUEVA LÓGICA CON ultima_venta_id
    ultima_venta_id = obtener_ultima_venta_id()

    crear_corte_caja(total_general, ultima_venta_id)

    return True, "Corte realizado correctamente"
