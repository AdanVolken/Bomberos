from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.styles import getSampleStyleSheet
from collections import defaultdict
from datetime import datetime


def generar_pdf_ventas(rows_filtrados, nombre_archivo="Resumen_Ventas.pdf"):

    if not rows_filtrados:
        return None

    # Agrupar por producto
    agrupado = defaultdict(lambda: {
        "unidades": 0,
        "total": 0
    })

    for row in rows_filtrados:
        producto = row["nombre"]
        agrupado[producto]["unidades"] += row["cantidad"]
        agrupado[producto]["total"] += row["total"]

    total_general = sum(data["total"] for data in agrupado.values())
    total_unidades = sum(data["unidades"] for data in agrupado.values())
    cantidad_ventas = len(rows_filtrados)
    promedio = total_general / cantidad_ventas if cantidad_ventas else 0

    doc = SimpleDocTemplate(nombre_archivo, pagesize=A4)
    elementos = []

    styles = getSampleStyleSheet()

    titulo_style = styles["Heading1"]
    normal_style = styles["Normal"]

    elementos.append(Paragraph("Resumen de Ventas", titulo_style))
    elementos.append(Spacer(1, 0.5 * cm))

    elementos.append(Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", normal_style))
    elementos.append(Spacer(1, 0.5 * cm))

    elementos.append(Paragraph(f"Total vendido: ${int(total_general):,}", normal_style))
    elementos.append(Paragraph(f"Unidades vendidas: {total_unidades}", normal_style))
    elementos.append(Paragraph(f"Cantidad de ventas: {cantidad_ventas}", normal_style))
    elementos.append(Paragraph(f"Promedio por venta: ${int(promedio):,}", normal_style))
    elementos.append(Spacer(1, 1 * cm))

    # Tabla detalle
    data = [["Producto", "Unidades", "Total ($)"]]

    for producto, info in agrupado.items():
        data.append([
            producto,
            info["unidades"],
            f"${int(info['total']):,}"
        ])

    tabla = Table(data, colWidths=[7 * cm, 3 * cm, 3 * cm])

    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
    ]))

    elementos.append(tabla)

    doc.build(elementos)

    return nombre_archivo
