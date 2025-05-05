from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
)

import os

BOT_TOKEN = os.environ['BOT_TOKEN']
TARGET_CHAT_ID = int(os.environ['TARGET_CHAT_ID'])
CONFIRM_TEXT = "✅ Дякуємо! Вашу новину отримано."

# Стани
WAITING_FOR_NEWS = {}

# Отримуємо порт, якщо він заданий
PORT = int(os.environ.get("PORT", 10000))  # Якщо не задано, використовуємо порт 10000

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📰 Надіслати новину", callback_data="send_news")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привіт! Натисніть кнопку нижче, щоб надіслати новину.", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    WAITING_FOR_NEWS[user_id] = True
    await query.message.reply_text("Будь ласка, надішліть текст, фото або відео новини:")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if WAITING_FOR_NEWS.get(user_id):
        # Визначаємо, що надіслав користувач
        if update.message.text:
            await context.bot.send_message(
                chat_id=TARGET_CHAT_ID,
                text=f"📝 Новина від @{update.effective_user.username or update.effective_user.first_name}:\n\n{update.message.text}"
            )
        elif update.message.photo:
            await context.bot.send_photo(
                chat_id=TARGET_CHAT_ID,
                photo=update.message.photo[-1].file_id,
                caption=f"🖼️ Фото від @{update.effective_user.username or update.effective_user.first_name}"
            )
        elif update.message.video:
            await context.bot.send_video(
                chat_id=TARGET_CHAT_ID,
                video=update.message.video.file_id,
                caption=f"📹 Відео від @{update.effective_user.username or update.effective_user.first_name}"
            )
        else:
            await update.message.reply_text("⚠️ Надішліть текст, фото або відео.")

        # Підтвердження
        await update.message.reply_text(CONFIRM_TEXT)
        WAITING_FOR_NEWS.pop(user_id, None)
    else:
        await update.message.reply_text("Натисніть кнопку “Надіслати новину” спочатку.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.ALL, message_handler))

    print("Бот запущено.")
    app.run_polling(port=PORT)  # Вказуємо порт для запуску
