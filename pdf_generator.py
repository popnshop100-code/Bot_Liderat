"""
Generador de PDF - Plantilla DINÁMICA Liderat UPV
Replica exactamente el template original.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph, Image
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

AZUL_OSCURO = colors.HexColor("#1F4E79")
AZUL_CLARO  = colors.HexColor("#9DC3E6")
BLANCO      = colors.white
NEGRO       = colors.HexColor("#1a1a1a")
GRIS_BORDE  = colors.HexColor("#cccccc")

LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "liderat_logo.png")
PAGE_W, PAGE_H = A4
MARGEN = 2 * cm


def generar_pdf_dinamica(datos: dict, ruta_salida: str):
    """
    datos = {
        titulo, objetivo, responsable, material,
        fecha, descripcion, feedback
    }
    """
    doc = SimpleDocTemplate(
        ruta_salida,
        pagesize=A4,
        leftMargin=MARGEN, rightMargin=MARGEN,
        topMargin=1.5 * cm, bottomMargin=MARGEN,
    )

    story = []
    ancho_util = PAGE_W - 2 * MARGEN

    # ── LOGO ────────────────────────────────────
    if os.path.exists(LOGO_PATH):
        logo = Image(LOGO_PATH, width=6 * cm, height=2 * cm)
        logo.hAlign = "LEFT"
        story.append(logo)
    story.append(Spacer(1, 0.4 * cm))

    # ── ESTILOS ──────────────────────────────────
    header_style = ParagraphStyle(
        "Header", fontName="Helvetica-Bold", fontSize=9,
        textColor=BLANCO, alignment=TA_CENTER, leading=12,
    )
    valor_style = ParagraphStyle(
        "Valor", fontName="Helvetica", fontSize=9,
        textColor=NEGRO, alignment=TA_LEFT, leading=13,
    )
    contenido_style = ParagraphStyle(
        "Contenido", fontName="Helvetica", fontSize=9,
        textColor=NEGRO, alignment=TA_LEFT, leading=13,
        spaceBefore=3, spaceAfter=3,
    )

    col_izq = ancho_util * 0.25
    col_der = ancho_util * 0.75
    h_header    = 0.65 * cm
    h_valor     = 0.75 * cm
    h_contenido = 3.8 * cm

    tabla_data = [
        # Fila 0: DINÁMICA (label azul claro) | título
        [Paragraph("DINÁMICA",        header_style),
         Paragraph(datos.get("titulo", ""), valor_style)],

        # Fila 1: OBJETIVO (label azul oscuro) | objetivo
        [Paragraph("OBJETIVO",        header_style),
         Paragraph(datos.get("objetivo", ""), valor_style)],

        # Fila 2: RESPONSABLE | MATERIAL ESTÁNDAR (ambos headers azul oscuro)
        [Paragraph("RESPONSABLE",     header_style),
         Paragraph("MATERIAL ESTÁNDAR", header_style)],

        # Fila 3: valor responsable | valor material
        [Paragraph(datos.get("responsable", ""), valor_style),
         Paragraph(datos.get("material", ""),    valor_style)],

        # Fila 4: FECHA (header azul oscuro izq) | vacío der
        [Paragraph("FECHA",           header_style),
         Paragraph("",                valor_style)],

        # Fila 5: valor fecha | vacío
        [Paragraph(datos.get("fecha", ""), valor_style),
         Paragraph("",                valor_style)],

        # Fila 6: DINÁMICA (header azul oscuro, full width)
        [Paragraph("DINÁMICA",        header_style),
         Paragraph("",                valor_style)],

        # Fila 7: descripción (full width)
        [Paragraph(datos.get("descripcion", ""), contenido_style),
         Paragraph("",                valor_style)],

        # Fila 8: FEEDBACK (header azul oscuro, full width)
        [Paragraph("FEEDBACK",        header_style),
         Paragraph("",                valor_style)],

        # Fila 9: feedback (full width)
        [Paragraph(datos.get("feedback", ""), contenido_style),
         Paragraph("",                valor_style)],
    ]

    alturas = [
        h_header,       # 0 DINÁMICA label
        h_header,       # 1 OBJETIVO label
        h_header,       # 2 RESPONSABLE | MATERIAL label
        h_valor,        # 3 valores responsable/material
        h_header,       # 4 FECHA label
        h_valor,        # 5 valor fecha
        h_header,       # 6 DINÁMICA contenido label
        h_contenido,    # 7 descripción
        h_header,       # 8 FEEDBACK label
        h_contenido,    # 9 feedback
    ]

    tabla = Table(tabla_data, colWidths=[col_izq, col_der], rowHeights=alturas)

    tabla.setStyle(TableStyle([
        # Bordes
        ("BOX",          (0, 0), (-1, -1), 0.5, GRIS_BORDE),
        ("INNERGRID",    (0, 0), (-1, -1), 0.5, GRIS_BORDE),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),

        # Fila 0: DINÁMICA — azul claro (izq) / blanco (der)
        ("BACKGROUND", (0, 0), (0, 0), AZUL_CLARO),
        ("BACKGROUND", (1, 0), (1, 0), BLANCO),

        # Fila 1: OBJETIVO — azul oscuro (izq) / blanco (der)
        ("BACKGROUND", (0, 1), (0, 1), AZUL_OSCURO),
        ("BACKGROUND", (1, 1), (1, 1), BLANCO),

        # Fila 2: RESPONSABLE | MATERIAL — azul oscuro full
        ("BACKGROUND", (0, 2), (-1, 2), AZUL_OSCURO),

        # Fila 3: valores — blanco
        ("BACKGROUND", (0, 3), (-1, 3), BLANCO),

        # Fila 4: FECHA — azul oscuro (izq) / blanco (der)
        ("BACKGROUND", (0, 4), (0, 4), AZUL_OSCURO),
        ("BACKGROUND", (1, 4), (1, 4), BLANCO),

        # Fila 5: valor fecha — blanco
        ("BACKGROUND", (0, 5), (-1, 5), BLANCO),

        # Fila 6: DINÁMICA header — azul oscuro, span full
        ("BACKGROUND", (0, 6), (-1, 6), AZUL_OSCURO),
        ("SPAN",       (0, 6), (-1, 6)),

        # Fila 7: descripción — blanco, span full, top
        ("BACKGROUND", (0, 7), (-1, 7), BLANCO),
        ("SPAN",       (0, 7), (-1, 7)),
        ("VALIGN",     (0, 7), (-1, 7), "TOP"),

        # Fila 8: FEEDBACK header — azul oscuro, span full
        ("BACKGROUND", (0, 8), (-1, 8), AZUL_OSCURO),
        ("SPAN",       (0, 8), (-1, 8)),

        # Fila 9: feedback — blanco, span full, top
        ("BACKGROUND", (0, 9), (-1, 9), BLANCO),
        ("SPAN",       (0, 9), (-1, 9)),
        ("VALIGN",     (0, 9), (-1, 9), "TOP"),
    ]))

    story.append(tabla)
    story.append(Spacer(1, 0.4 * cm))

    pie_style = ParagraphStyle(
        "Pie", fontName="Helvetica", fontSize=7,
        textColor=colors.HexColor("#888888"), alignment=TA_CENTER,
    )
    story.append(Paragraph(
        "Liderat UPV · Asociación Juvenil · Documento generado automáticamente",
        pie_style
    ))

    doc.build(story)
    print(f"✅ PDF generado: {ruta_salida}")
