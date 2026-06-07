"""
Bot de Telegram - Liderat UPV
Genera PDFs: DINÁMICA y FICHA EVENTO
"""

import os
import logging
import calendar
import tempfile
import threading
from datetime import date, datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters, ContextTypes
)
from pdf_generator import generar_pdf_dinamica
from pdf_ficha_evento import generar_pdf_ficha_evento

# ── SERVER HTTP (para Render) ─────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, format, *args):
        pass

def run_server():
    HTTPServer(("0.0.0.0", 10000), Handler).serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# ── LOGGING ──────────────────────────────────────────────────
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("8650563136:AAEGC5CrmW0fYhfPlf_ea1Sa85UU2eAY4TI", "8650563136:AAEGC5CrmW0fYhfPlf_ea1Sa85UU2eAY4TI")

# ── ESTADOS DINÁMICA ─────────────────────────────────────────
(
    SELECCIONAR_TIPO,
    # Dinámica
    D_TITULO, D_OBJETIVO, D_RESPONSABLE, D_MATERIAL, D_FECHA, D_DESCRIPCION, D_FEEDBACK,
    # Ficha Evento
    FE_TITULO, FE_DESCRIPCION, FE_RESPONSABLE, FE_FECHA, FE_HORARIO,
    FE_LUGAR, FE_PUBLICO, FE_AFORO, FE_RECURSOS_NEC, FE_RECURSOS_DISP,
    FE_COLABORACION, FE_NECESITAS_GE, FE_PRESUPUESTO, FE_OTROS,
) = range(22)

# ── CALENDARIO ───────────────────────────────────────────────
MESES_ES = ["","Enero","Febrero","Marzo","Abril","Mayo","Junio",
            "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

def build_calendar(year: int, month: int) -> InlineKeyboardMarkup:
    teclado = []
    teclado.append([
        InlineKeyboardButton("◀", callback_data=f"cal_prev_{year}_{month}"),
        InlineKeyboardButton(f"{MESES_ES[month]} {year}", callback_data="cal_ignore"),
        InlineKeyboardButton("▶", callback_data=f"cal_next_{year}_{month}"),
    ])
    teclado.append([InlineKeyboardButton(d, callback_data="cal_ignore")
                    for d in ["L","M","X","J","V","S","D"]])
    for semana in calendar.monthcalendar(year, month):
        fila = []
        for dia in semana:
            if dia == 0:
                fila.append(InlineKeyboardButton(" ", callback_data="cal_ignore"))
            else:
                fila.append(InlineKeyboardButton(str(dia), callback_data=f"cal_dia_{year}_{month}_{dia}"))
        teclado.append(fila)
    return InlineKeyboardMarkup(teclado)


async def calendario_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "cal_ignore":
        return context.user_data.get("cal_state")
    partes = data.split("_")
    if partes[1] == "prev":
        year, month = int(partes[2]), int(partes[3])
        month -= 1
        if month < 1: month, year = 12, year - 1
        await query.edit_message_reply_markup(reply_markup=build_calendar(year, month))
        return context.user_data.get("cal_state")
    if partes[1] == "next":
        year, month = int(partes[2]), int(partes[3])
        month += 1
        if month > 12: month, year = 1, year + 1
        await query.edit_message_reply_markup(reply_markup=build_calendar(year, month))
        return context.user_data.get("cal_state")
    if partes[1] == "dia":
        year, month, day = int(partes[2]), int(partes[3]), int(partes[4])
        fecha_str = f"{day:02d}/{month:02d}/{year}"
        context.user_data["fecha"] = fecha_str
        await query.edit_message_text(f"📅 Fecha seleccionada: *{fecha_str}*", parse_mode="Markdown")
        next_state = context.user_data.get("cal_next_state")
        next_msg   = context.user_data.get("cal_next_msg", "Continúa:")
        await query.message.reply_text(next_msg, parse_mode="Markdown")
        return next_state
    return context.user_data.get("cal_state")


async def mostrar_calendario(update, context, state, next_state, next_msg):
    hoy = date.today()
    context.user_data["cal_state"] = state
    context.user_data["cal_next_state"] = next_state
    context.user_data["cal_next_msg"] = next_msg
    await update.message.reply_text(
        "📅 *¿Qué fecha fue? Selecciónala:*",
        parse_mode="Markdown",
        reply_markup=build_calendar(hoy.year, hoy.month),
    )
    return state


# ── INICIO ───────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    teclado = [["📋 DINÁMICA", "📅 FICHA EVENTO"]]
    markup = ReplyKeyboardMarkup(teclado, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        "👋 ¡Hola! Soy el bot de *Liderat UPV*.\n\n¿Qué tipo de documento quieres generar?",
        parse_mode="Markdown",
        reply_markup=markup,
    )
    return SELECCIONAR_TIPO


async def seleccionar_tipo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    tipo = update.message.text
    context.user_data["tipo"] = tipo
    if "DINÁMICA" in tipo:
        await update.message.reply_text("✏️ *¿Cuál es el título de la dinámica?*",
                                        parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
        return D_TITULO
    else:
        await update.message.reply_text("✏️ *¿Cuál es el título del evento?*",
                                        parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
        return FE_TITULO


# ════════════════════════════════════════════════════════════
#  FLUJO DINÁMICA
# ════════════════════════════════════════════════════════════

async def d_titulo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["titulo"] = update.message.text
    await update.message.reply_text("🎯 *¿Cuál es el objetivo de la dinámica?*", parse_mode="Markdown")
    return D_OBJETIVO

async def d_objetivo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["objetivo"] = update.message.text
    await update.message.reply_text("👤 *¿Quién es el responsable?*", parse_mode="Markdown")
    return D_RESPONSABLE

async def d_responsable(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["responsable"] = update.message.text
    await update.message.reply_text("🧰 *¿Qué material estándar se utiliza?*", parse_mode="Markdown")
    return D_MATERIAL

async def d_material(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["material"] = update.message.text
    return await mostrar_calendario(update, context, D_FECHA, D_DESCRIPCION,
        "📝 *Descripción de la dinámica*\n\nCuéntame cómo fue:")

async def d_descripcion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["descripcion"] = update.message.text
    await update.message.reply_text("💬 *¿Cuál fue el feedback de la dinámica?*", parse_mode="Markdown")
    return D_FEEDBACK

async def d_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["feedback"] = update.message.text
    await update.message.reply_text("⏳ Generando PDF...")
    datos = {
        "titulo":      context.user_data.get("titulo", ""),
        "objetivo":    context.user_data.get("objetivo", ""),
        "responsable": context.user_data.get("responsable", ""),
        "material":    context.user_data.get("material", ""),
        "fecha":       context.user_data.get("fecha", ""),
        "descripcion": context.user_data.get("descripcion", ""),
        "feedback":    context.user_data.get("feedback", ""),
    }
    ruta = os.path.join(tempfile.gettempdir(), f"dinamica_{update.effective_user.id}.pdf")
    generar_pdf_dinamica(datos, ruta)
    nombre = f"Dinamica_{datos['titulo'].replace(' ','_')}_{datos['fecha'].replace('/','-')}.pdf"
    with open(ruta, "rb") as f:
        await update.message.reply_document(document=f, filename=nombre,
            caption=f"✅ *{datos['titulo']}* — {datos['fecha']}", parse_mode="Markdown")
    await update.message.reply_text("¿Otro documento? Usa /start")
    context.user_data.clear()
    return ConversationHandler.END


# ════════════════════════════════════════════════════════════
#  FLUJO FICHA EVENTO
# ════════════════════════════════════════════════════════════

async def fe_titulo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["titulo"] = update.message.text
    await update.message.reply_text("📝 *Describe brevemente la idea general del evento:*", parse_mode="Markdown")
    return FE_DESCRIPCION

async def fe_descripcion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["descripcion"] = update.message.text
    await update.message.reply_text(
        "👤 *¿Quién es el profesor/tutor responsable?*\n\n(Nombre, cargo y departamento)", parse_mode="Markdown")
    return FE_RESPONSABLE

async def fe_responsable(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["responsable"] = update.message.text
    return await mostrar_calendario(update, context, FE_FECHA, FE_HORARIO,
        "🕐 *¿Cuál es el horario del evento?*\n\n(Ej: 18:30 a 20:30, duración 2 horas)")

async def fe_horario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["horario"] = update.message.text
    await update.message.reply_text("📍 *¿Dónde se realizará el evento?*", parse_mode="Markdown")
    return FE_LUGAR

async def fe_lugar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["lugar"] = update.message.text
    await update.message.reply_text("🎓 *¿A qué público va dirigido?*", parse_mode="Markdown")
    return FE_PUBLICO

async def fe_publico(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["publico"] = update.message.text
    await update.message.reply_text("👥 *¿Cuántas personas se esperan / cuál es el aforo?*", parse_mode="Markdown")
    return FE_AFORO

async def fe_aforo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["aforo"] = update.message.text
    await update.message.reply_text("🔧 *¿Qué recursos se necesitan?*\n\n(Logística, técnico, audiovisual...)", parse_mode="Markdown")
    return FE_RECURSOS_NEC

async def fe_recursos_nec(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["recursos_necesarios"] = update.message.text
    await update.message.reply_text("✅ *¿Con qué recursos contáis ya?*\n\n(Ponentes, moderador, material...)", parse_mode="Markdown")
    return FE_RECURSOS_DISP

async def fe_recursos_disp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["recursos_disponibles"] = update.message.text
    teclado = [["✅ Sí", "❌ No"]]
    markup = ReplyKeyboardMarkup(teclado, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("🤝 *¿Vais a colaborar con otros equipos de GE?*", parse_mode="Markdown", reply_markup=markup)
    return FE_COLABORACION

async def fe_colaboracion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    respuesta = update.message.text
    if "No" in respuesta or "❌" in respuesta:
        context.user_data["colaboracion"] = "No se prevé la colaboración en este evento."
    else:
        context.user_data["colaboracion"] = respuesta
    await update.message.reply_text("📋 *¿Qué necesitáis de GE?*", parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
    return FE_NECESITAS_GE

async def fe_necesitas_ge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["necesitas_ge"] = update.message.text
    await update.message.reply_text("💰 *Presupuesto de ingresos y gastos:*", parse_mode="Markdown")
    return FE_PRESUPUESTO

async def fe_presupuesto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["presupuesto"] = update.message.text
    await update.message.reply_text("📎 *Otros (derechos de imagen, grabación, señalética...):*\n\nEscribe 'ninguno' si no hay nada más.", parse_mode="Markdown")
    return FE_OTROS

async def fe_otros(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    otros = update.message.text
    if otros.lower() == "ninguno":
        otros = ""
    context.user_data["otros"] = otros

    await update.message.reply_text("⏳ Generando ficha de evento...")

    datos = {
        "titulo":               context.user_data.get("titulo", ""),
        "descripcion":          context.user_data.get("descripcion", ""),
        "responsable":          context.user_data.get("responsable", ""),
        "fecha":                context.user_data.get("fecha", ""),
        "horario":              context.user_data.get("horario", ""),
        "lugar":                context.user_data.get("lugar", ""),
        "publico":              context.user_data.get("publico", ""),
        "aforo":                context.user_data.get("aforo", ""),
        "recursos_necesarios":  context.user_data.get("recursos_necesarios", ""),
        "recursos_disponibles": context.user_data.get("recursos_disponibles", ""),
        "colaboracion":         context.user_data.get("colaboracion", ""),
        "necesitas_ge":         context.user_data.get("necesitas_ge", ""),
        "presupuesto":          context.user_data.get("presupuesto", ""),
        "otros":                context.user_data.get("otros", ""),
    }

    ruta = os.path.join(tempfile.gettempdir(), f"ficha_{update.effective_user.id}.pdf")
    generar_pdf_ficha_evento(datos, ruta)

    titulo_limpio = datos["titulo"].replace(" ", "_")
    nombre = f"Ficha_Eventos_LideraT_{titulo_limpio}.pdf"

    with open(ruta, "rb") as f:
        await update.message.reply_document(document=f, filename=nombre,
            caption=f"✅ *{datos['titulo']}*\n\nFicha lista para enviar a generacionespontanea@upv.es",
            parse_mode="Markdown")

    await update.message.reply_text("¿Otro documento? Usa /start")
    context.user_data.clear()
    return ConversationHandler.END


# ── CANCELAR ─────────────────────────────────────────────────
async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text("❌ Cancelado. Usa /start cuando quieras.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


# ── MAIN ─────────────────────────────────────────────────────
def main():
    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECCIONAR_TIPO: [MessageHandler(filters.TEXT & ~filters.COMMAND, seleccionar_tipo)],

            # Dinámica
            D_TITULO:      [MessageHandler(filters.TEXT & ~filters.COMMAND, d_titulo)],
            D_OBJETIVO:    [MessageHandler(filters.TEXT & ~filters.COMMAND, d_objetivo)],
            D_RESPONSABLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, d_responsable)],
            D_MATERIAL:    [MessageHandler(filters.TEXT & ~filters.COMMAND, d_material)],
            D_FECHA:       [CallbackQueryHandler(calendario_handler, pattern="^cal_")],
            D_DESCRIPCION: [MessageHandler(filters.TEXT & ~filters.COMMAND, d_descripcion)],
            D_FEEDBACK:    [MessageHandler(filters.TEXT & ~filters.COMMAND, d_feedback)],

            # Ficha Evento
            FE_TITULO:          [MessageHandler(filters.TEXT & ~filters.COMMAND, fe_titulo)],
            FE_DESCRIPCION:     [MessageHandler(filters.TEXT & ~filters.COMMAND, fe_descripcion)],
            FE_RESPONSABLE:     [MessageHandler(filters.TEXT & ~filters.COMMAND, fe_responsable)],
            FE_FECHA:           [CallbackQueryHandler(calendario_handler, pattern="^cal_")],
            FE_HORARIO:         [MessageHandler(filters.TEXT & ~filters.COMMAND, fe_horario)],
            FE_LUGAR:           [MessageHandler(filters.TEXT & ~filters.COMMAND, fe_lugar)],
            FE_PUBLICO:         [MessageHandler(filters.TEXT & ~filters.COMMAND, fe_publico)],
            FE_AFORO:           [MessageHandler(filters.TEXT & ~filters.COMMAND, fe_aforo)],
            FE_RECURSOS_NEC:    [MessageHandler(filters.TEXT & ~filters.COMMAND, fe_recursos_nec)],
            FE_RECURSOS_DISP:   [MessageHandler(filters.TEXT & ~filters.COMMAND, fe_recursos_disp)],
            FE_COLABORACION:    [MessageHandler(filters.TEXT & ~filters.COMMAND, fe_colaboracion)],
            FE_NECESITAS_GE:    [MessageHandler(filters.TEXT & ~filters.COMMAND, fe_necesitas_ge)],
            FE_PRESUPUESTO:     [MessageHandler(filters.TEXT & ~filters.COMMAND, fe_presupuesto)],
            FE_OTROS:           [MessageHandler(filters.TEXT & ~filters.COMMAND, fe_otros)],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    app.add_handler(conv)
    logger.info("🚀 Bot iniciado")
    app.run_polling()


if __name__ == "__main__":
    main()
