"""
Generador de PDF - Ficha Eventos LideraT UPV
Replica exactamente el documento de Generación Espontánea UPV
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_UPV = os.path.join(BASE_DIR, "LOGOUPV.png")
LOGO_GE  = os.path.join(BASE_DIR, "GELOGO.png")

PAGE_W, PAGE_H = A4
MARGEN = 2.5 * cm


def generar_pdf_ficha_evento(datos: dict, ruta_salida: str):
    """
    datos = {
        titulo, descripcion, responsable, fecha, horario,
        lugar, publico, aforo, recursos_necesarios,
        recursos_disponibles, colaboracion, necesitas_ge,
        presupuesto, otros
    }
    """
    doc = SimpleDocTemplate(
        ruta_salida,
        pagesize=A4,
        leftMargin=MARGEN,
        rightMargin=MARGEN,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    story = []
    ancho_util = PAGE_W - 2 * MARGEN

    # ── ESTILOS ──────────────────────────────────────────────
    titulo_doc = ParagraphStyle(
        "TituloDoc", fontName="Helvetica-Bold", fontSize=13,
        textColor=colors.black, alignment=TA_CENTER, leading=18,
        spaceBefore=10, spaceAfter=6,
    )
    subtitulo = ParagraphStyle(
        "Subtitulo", fontName="Helvetica-Bold", fontSize=10,
        textColor=colors.black, alignment=TA_JUSTIFY, leading=14,
        spaceBefore=8, spaceAfter=4,
    )
    body = ParagraphStyle(
        "Body", fontName="Helvetica", fontSize=10,
        textColor=colors.black, alignment=TA_JUSTIFY, leading=14,
        spaceBefore=2, spaceAfter=4,
    )
    label = ParagraphStyle(
        "Label", fontName="Helvetica-Bold", fontSize=10,
        textColor=colors.black, alignment=TA_LEFT, leading=14,
    )
    firma = ParagraphStyle(
        "Firma", fontName="Helvetica-Bold", fontSize=10,
        textColor=colors.black, alignment=TA_LEFT, leading=14,
        spaceBefore=20,
    )
    enviar = ParagraphStyle(
        "Enviar", fontName="Helvetica-Bold", fontSize=11,
        textColor=colors.black, alignment=TA_CENTER, leading=16,
        spaceBefore=30,
    )

    # ── CABECERA CON LOGOS ────────────────────────────────────
    logos = []
    if os.path.exists(LOGO_UPV):
        logos.append(Image(LOGO_UPV, width=4.5*cm, height=2*cm))
    else:
        logos.append(Paragraph("", body))

    if os.path.exists(LOGO_GE):
        logos.append(Image(LOGO_GE, width=4*cm, height=2*cm))
    else:
        logos.append(Paragraph("", body))

    tabla_logos = Table(
        [logos],
        colWidths=[ancho_util * 0.5, ancho_util * 0.5],
    )
    tabla_logos.setStyle(TableStyle([
        ("ALIGN",  (0, 0), (0, 0), "LEFT"),
        ("ALIGN",  (1, 0), (1, 0), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(tabla_logos)
    story.append(Spacer(1, 0.5 * cm))

    # ── TÍTULO PRINCIPAL ──────────────────────────────────────
    story.append(Paragraph("<u>ORGANIZACIÓN DE ACTIVIDADES Y EVENTOS</u>", titulo_doc))
    story.append(Spacer(1, 0.3 * cm))

    # ── INDICACIONES ──────────────────────────────────────────
    story.append(Paragraph(
        "<b>Indicaciones para la organización de eventos y actividades de Generación Espontánea:</b>",
        subtitulo
    ))
    indicaciones = [
        ("<b>Fechas</b>", "Se recomienda reservar con la mayor antelación posible, porque los salones de actos están muy demandados, evitando vacaciones y fechas en las que la universidad esté cerrada."),
        ("<b>Horario</b>", "los eventos deberán realizarse en horario normal de los campus, evitando cuando estén cerrados los días festivos o fines de semana."),
        ("<b>Sede</b>", "Las instalaciones de la universidad están a disposición para realizar actividades, pero se gestionan de diferente manera."),
        ("", "Los salones de actos centrales están centralizados, y se reservan a través de Asuntos Generales. Las reservas de aulas de las escuelas se pueden tramitar con vuestros tutores/as a través de las subdirecciones de Generación Espontánea, o quienes os indiquen."),
        ("<b>Autorizaciones</b>", "Para realizar actividades que requieran autorización, hay que enviar la propuesta de actividad con una semana al menos, de antelación a la realización del evento. Si el evento es complejo, se deberá enviar con antelación de un mes a su realización."),
        ("<b>Invitaciones</b>", "se recomienda invitar a las personas que tengan que ver con el equipo y el programa, así como patrocinadoras y empresas relacionadas con el equipo."),
        ("<b>Financiación</b>", "Se deberá presentar un presupuesto de ingresos y gastos, indicando la viabilidad del evento."),
    ]
    for etiqueta, texto in indicaciones:
        if etiqueta:
            story.append(Paragraph(f"{etiqueta}: {texto}", body))
        else:
            story.append(Paragraph(texto, body))

    story.append(Spacer(1, 0.5 * cm))

    # ── DATOS DEL EVENTO ──────────────────────────────────────
    story.append(Paragraph("<u>DATOS DE LA ACTIVIDAD O EVENTO</u>", titulo_doc))
    story.append(Spacer(1, 0.3 * cm))

    def seccion(numero, titulo_sec, contenido):
        story.append(Paragraph(f"<b>{numero}.- {titulo_sec}</b>", label))
        story.append(Spacer(1, 0.2 * cm))
        if isinstance(contenido, list):
            for linea in contenido:
                story.append(Paragraph(linea, body))
        else:
            story.append(Paragraph(contenido, body))
        story.append(Spacer(1, 0.4 * cm))

    # 1. Título y descripción
    story.append(Paragraph("<b>1.- Título y explicación del evento</b>", label))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(f"<b>Título del evento:</b> {datos.get('titulo', '')}", body))
    story.append(Spacer(1, 0.1*cm))
    story.append(Paragraph(f"<b>Idea general:</b> {datos.get('descripcion', '')}", body))
    story.append(Spacer(1, 0.4*cm))

    # 2. Responsable
    story.append(Paragraph("<b>2.-Profesor/a o entidad responsable</b>", label))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(datos.get('responsable', ''), body))
    story.append(Spacer(1, 0.4*cm))

    # 3. Fecha
    story.append(Paragraph("<b>3.- Fecha del evento</b>", label))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(f"La fecha prevista para la realización del evento es el {datos.get('fecha', '')}.", body))
    story.append(Paragraph(f"El horario estimado es de {datos.get('horario', '')}", body))
    story.append(Spacer(1, 0.4*cm))

    # 4. Lugar
    story.append(Paragraph("<b>4.- Lugar en el que se pretende realizar</b>", label))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(datos.get('lugar', ''), body))
    story.append(Spacer(1, 0.4*cm))

    # 5. Público
    story.append(Paragraph("<b>5.-Público al que va dirigido</b>", label))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(datos.get('publico', ''), body))
    story.append(Spacer(1, 0.4*cm))

    # 6. Aforo
    story.append(Paragraph("<b>6.- Número de personas esperadas</b>", label))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(datos.get('aforo', ''), body))
    story.append(Spacer(1, 0.4*cm))

    # 7. Recursos necesarios
    story.append(Paragraph("<b>7.- ¿Qué recursos se necesitan?</b>", label))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(datos.get('recursos_necesarios', ''), body))
    story.append(Spacer(1, 0.4*cm))

    # 8. Recursos disponibles
    story.append(Paragraph("<b>8.- ¿Con qué recursos contáis?</b>", label))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(datos.get('recursos_disponibles', ''), body))
    story.append(Spacer(1, 0.4*cm))

    # 9. Colaboración
    story.append(Paragraph("<b>9.- ¿Vais a colaborar con otro/s equipos de GE?</b>", label))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(datos.get('colaboracion', ''), body))
    story.append(Spacer(1, 0.4*cm))

    # 10. Necesitas de GE
    story.append(Paragraph("<b>10.- ¿Qué necesitas de GE?</b>", label))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(datos.get('necesitas_ge', ''), body))
    story.append(Spacer(1, 0.4*cm))

    # 11. Presupuesto
    story.append(Paragraph("<b>11.- Presupuesto de ingresos y gastos</b>", label))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(datos.get('presupuesto', ''), body))
    story.append(Spacer(1, 0.4*cm))

    # 12. Otros
    story.append(Paragraph("<b>12.-Otros</b>", label))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(datos.get('otros', ''), body))
    story.append(Spacer(1, 0.6*cm))

    # ── FIRMA Y ENVÍO ─────────────────────────────────────────
    story.append(Paragraph("<b>Fdo. Tutor/a del equipo</b>", firma))
    story.append(Spacer(1, 1.5*cm))
    story.append(Paragraph("<b>Enviar a: generacionespontanea@upv.es</b>", enviar))

    doc.build(story)
    print(f"✅ Ficha evento generada: {ruta_salida}")
