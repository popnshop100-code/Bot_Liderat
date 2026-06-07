"""
Bot de Telegram - Liderat UPV
Genera PDFs de dinámicas con flujo guiado + calendario
"""

import os
import logging
import calendar
import tempfile
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

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
from datetime import date, datetime

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters, ContextTypes
)
from pdf_generator import generar_pdf_dinamica

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("8650563136:AAEGC5CrmW0fYhfPlf_ea1Sa85UU2eAY4TI", "8650563136:AAEGC5CrmW0fYhfPlf_ea1Sa85UU2eAY4TI")

# Estados
(
    SELECCIONAR_TIPO,
    TITULO,
    OBJETIVO,
    RESPONSABLE,
    MATERIAL,
    FECHA_CAL,
    DESCRIPCION,
    FEEDBACK,
) = range(8)


# ─────────────────────────────────────────────
#  CALENDARIO
# ─────────────────────────────────────────────

MESES_ES = [
    "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

def build_calendar(year: int, month: int) -> InlineKeyboardMarkup:
    teclado = []

    # Cabecera con navegación
    teclado.append([
        InlineKeyboardButton("◀", callback_data=f"cal_prev_{year}_{month}"),
        InlineKeyboardButton(f"{MESES_ES[month]} {year}", callback_data="cal_ignore"),
        InlineKeyboardButton("▶", callback_data=f"cal_next_{year}_{month}"),
    ])

    # Días de la semana
    teclado.append([
        InlineKeyboardButton(d, callback_data="cal_ignore")
        for d in ["L", "M", "X", "J", "V", "S", "D"]
    ])

    # Días del mes
    for semana in calendar.monthcalendar(year, month):
        fila = []
        for dia in semana:
            if dia == 0:
                fila.append(InlineKeyboardButton(" ", callback_data="cal_ignore"))
            else:
                fila.append(InlineKeyboardButton(
                    str(dia),
                    callback_data=f"cal_dia_{year}_{month}_{dia}"
                ))
        teclado.append(fila)

    return InlineKeyboardMarkup(teclado)


async def calendario_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "cal_ignore":
        return FECHA_CAL

    partes = data.split("_")

    if partes[1] == "prev":
        year, month = int(partes[2]), int(partes[3])
        month -= 1
        if month < 1:
            month = 12
            year -= 1
        await query.edit_message_reply_markup(reply_markup=build_calendar(year, month))
        return FECHA_CAL

    if partes[1] == "next":
        year, month = int(partes[2]), int(partes[3])
        month += 1
        if month > 12:
            month = 1
            year += 1
        await query.edit_message_reply_markup(reply_markup=build_calendar(year, month))
        return FECHA_CAL

    if partes[1] == "dia":
        year, month, day = int(partes[2]), int(partes[3]), int(partes[4])
        fecha_str = f"{day:02d}/{month:02d}/{year}"
        context.user_data["fecha"] = fecha_str

        await query.edit_message_text(f"📅 Fecha seleccionada: *{fecha_str}*", parse_mode="Markdown")

        await query.message.reply_text(
            "📝 *Descripción de la dinámica*\n\nCuéntame cómo fue:",
            parse_mode="Markdown",
        )
        return DESCRIPCION

    return FECHA_CAL


# ─────────────────────────────────────────────
#  FLUJO PRINCIPAL
# ─────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    teclado = [["📋 DINÁMICA"]]
    markup = ReplyKeyboardMarkup(teclado, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text(
        "👋 ¡Hola! Soy el bot de *Liderat UPV*.\n\n¿Qué tipo de documento quieres generar?",
        parse_mode="Markdown",
        reply_markup=markup,
    )
    return SELECCIONAR_TIPO


async def seleccionar_tipo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["tipo"] = update.message.text
    await update.message.reply_text(
        "✏️ *¿Cuál es el título de la dinámica?*",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
    return TITULO


async def titulo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["titulo"] = update.message.text
    await update.message.reply_text(
        "🎯 *¿Cuál es el objetivo de la dinámica?*",
        parse_mode="Markdown",
    )
    return OBJETIVO


async def objetivo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["objetivo"] = update.message.text
    await update.message.reply_text(
        "👤 *¿Quién es el responsable?*",
        parse_mode="Markdown",
    )
    return RESPONSABLE


async def responsable(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["responsable"] = update.message.text
    await update.message.reply_text(
        "🧰 *¿Qué material estándar se utiliza?*",
        parse_mode="Markdown",
    )
    return MATERIAL


async def material(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["material"] = update.message.text

    hoy = date.today()
    await update.message.reply_text(
        "📅 *¿Qué fecha fue? Selecciónala en el calendario:*",
        parse_mode="Markdown",
        reply_markup=build_calendar(hoy.year, hoy.month),
    )
    return FECHA_CAL


async def descripcion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["descripcion"] = update.message.text
    await update.message.reply_text(
        "💬 *¿Cuál fue el feedback de la dinámica?*",
        parse_mode="Markdown",
    )
    return FEEDBACK


async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["feedback"] = update.message.text

    datos = context.user_data
    await update.message.reply_text(
        f"✅ *Resumen:*\n\n"
        f"📋 Título: {datos.get('titulo')}\n"
        f"🎯 Objetivo: {datos.get('objetivo')}\n"
        f"👤 Responsable: {datos.get('responsable')}\n"
        f"🧰 Material: {datos.get('material')}\n"
        f"📅 Fecha: {datos.get('fecha')}\n\n"
        f"⏳ Generando PDF...",
        parse_mode="Markdown",
    )

    datos_pdf = {
        "titulo":      datos.get("titulo", ""),
        "objetivo":    datos.get("objetivo", ""),
        "responsable": datos.get("responsable", ""),
        "material":    datos.get("material", ""),
        "fecha":       datos.get("fecha", ""),
        "descripcion": datos.get("descripcion", ""),
        "feedback":    datos.get("feedback", ""),
    }

    ruta_pdf = os.path.join(tempfile.gettempdir(), f"dinamica_{update.effective_user.id}.pdf")
    generar_pdf_dinamica(datos_pdf, ruta_pdf)

    with open(ruta_pdf, "rb") as pdf:
        await update.message.reply_document(
            document=pdf,
            filename=f"Dinamica_{datos_pdf['titulo'].replace(' ', '_')}_{datos_pdf['fecha'].replace('/', '-')}.pdf",
            caption=f"✅ *{datos_pdf['titulo']}* — {datos_pdf['fecha']}\n\nGenerado por LideraT Bot.",
            parse_mode="Markdown",
        )

    await update.message.reply_text("¿Quieres generar otro documento? Usa /start")
    context.user_data.clear()
    return ConversationHandler.END


# ─────────────────────────────────────────────
#  CANCELAR
# ─────────────────────────────────────────────

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text("❌ Cancelado. Usa /start cuando quieras.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────

def main():
    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECCIONAR_TIPO: [MessageHandler(filters.TEXT & ~filters.COMMAND, seleccionar_tipo)],
            TITULO:           [MessageHandler(filters.TEXT & ~filters.COMMAND, titulo)],
            OBJETIVO:         [MessageHandler(filters.TEXT & ~filters.COMMAND, objetivo)],
            RESPONSABLE:      [MessageHandler(filters.TEXT & ~filters.COMMAND, responsable)],
            MATERIAL:         [MessageHandler(filters.TEXT & ~filters.COMMAND, material)],
            FECHA_CAL:        [CallbackQueryHandler(calendario_handler, pattern="^cal_")],
            DESCRIPCION:      [MessageHandler(filters.TEXT & ~filters.COMMAND, descripcion)],
            FEEDBACK:         [MessageHandler(filters.TEXT & ~filters.COMMAND, feedback)],
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    app.add_handler(conv)
    logger.info("🚀 Bot iniciado")
    app.run_polling()


if __name__ == "__main__":
    main()
