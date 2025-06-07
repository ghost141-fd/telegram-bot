from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
import os

# Твой Telegram ID для админских команд
ADMIN_ID = 1572671116  # Заменить на свой ID

# Для хранения данных пользователей
user_data = {}

# Сохраняем chat_id в файл
def save_user(chat_id):
    if not os.path.exists("users.txt"):
        with open("users.txt", "w") as f:
            f.write(str(chat_id) + "\n")
    else:
        with open("users.txt", "r+") as f:
            ids = f.read().splitlines()
            if str(chat_id) not in ids:
                f.write(str(chat_id) + "\n")

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    save_user(chat_id)
    await update.message.reply_text("Привет, я бот и рассчитаю стоимость продвижения.\nНапишите вашу нишу 👇")

# Обработка ниши
async def handle_niche(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user_data[chat_id] = {"niche": update.message.text}
    save_user(chat_id)

    text = (
        "🔹 *Тариф Лайт* — Упакуем карточку, удалим негатив и дадим рекомендации.\n\n"
        "🔹 *Тариф Стандарт* — Всё, что в Лайт + продвижение в топ-3 на Яндекс.Картах и Яндекс.Поиске + работа с 2GIS.\n\n"
        "🔹 *Тариф Премиум* — Всё, что в Стандарт + SEO и гарантированный топ-1 среди конкурентов.\n\n"
        "Выберите тариф:"
    )

    keyboard = [
        [InlineKeyboardButton("Лайт", callback_data="Лайт")],
        [InlineKeyboardButton("Стандарт", callback_data="Стандарт")],
        [InlineKeyboardButton("Премиум", callback_data="Премиум")],
    ]

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# Выбор тарифа
async def handle_tariff_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id
    tariff = query.data
    niche = user_data.get(chat_id, {}).get("niche", "не указана")

    prices = {
        "Лайт": "13 990₽",
        "Стандарт": "19 990₽",
        "Премиум": "26 990₽"
    }

    price = prices.get(tariff, "неизвестна")

    result = (
        f"🔍 Ваша ниша — *{niche}*\n"
        f"Вы выбрали тариф — *{tariff}*\n"
        f"💰 Стоимость: *{price}*\n\n"
        "🎁 *Скидка 20%* на второй месяц продвижения!"
    )

    keyboard = [
        [InlineKeyboardButton("📲 Связаться с менеджером", url="https://t.me/Goust_141OTG")]
    ]

    await query.message.reply_text(
        result,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Команда рассылки текстом всем пользователям
async def send_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ У вас нет прав для этой команды.")
        return

    if context.args:
        message = " ".join(context.args)
        sent = 0

        if not os.path.exists("users.txt"):
            await update.message.reply_text("Нет ни одного пользователя в базе.")
            return

        with open("users.txt", "r") as f:
            ids = f.read().splitlines()

        for user_id in ids:
            try:
                await context.bot.send_message(chat_id=int(user_id), text=message)
                sent += 1
            except:
                pass

        await update.message.reply_text(f"✅ Сообщение отправлено {sent} пользователям.")
    else:
        await update.message.reply_text("Введите сообщение: /sendall текст")

# Команда рассылки с фото + кнопкой "Связаться с менеджером"
async def send_all_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ У вас нет прав для этой команды.")
        return

    # Здесь поставь свою ссылку на картинку
    photo_url = "https://cdn-icons-png.flaticon.com/512/732/732200.png"

    caption = "🔥 Новое предложение! Закажи продвижение на Яндекс.Картах сейчас!"

    keyboard = [
        [InlineKeyboardButton("📲 Связаться с менеджером", url="https://t.me/Goust_141OTG")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if not os.path.exists("users.txt"):
        await update.message.reply_text("Нет ни одного пользователя в базе.")
        return

    with open("users.txt", "r") as f:
        ids = f.read().splitlines()

    sent = 0
    for user_id in ids:
        try:
            await context.bot.send_photo(
                chat_id=int(user_id),
                photo=photo_url,
                caption=caption,
                reply_markup=reply_markup
            )
            sent += 1
        except Exception as e:
            print(f"Не удалось отправить {user_id}: {e}")

    await update.message.reply_text(f"✅ Фото-рассылка отправлена {sent} пользователям.")

# Главная функция
def main():
    app = ApplicationBuilder().token("7486297110:AAGJJfbEzgUcHmETvGjCZp-aRd-4T0V5qaI").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_niche))
    app.add_handler(CallbackQueryHandler(handle_tariff_choice))
    app.add_handler(CommandHandler("sendall", send_all))
    app.add_handler(CommandHandler("sendallphoto", send_all_photo))

    print("🤖 Бот запущен! t.me/YandexCartBot")
    app.run_polling()

if __name__ == "__main__":
    main()
