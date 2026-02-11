import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from groq import Groq

# --- КЛЮЧИ ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

# --- ХРАНИЛИЩЕ ЗАПРОСОВ ---
user_requests = {}

# --- МЕНЮ ---
menu = ReplyKeyboardMarkup(
    [
        ["📉 Почему нет продаж", "🛍 Улучшить карточку"],
        ["📊 Анализ ниши", "💰 Расчёт прибыли"],
        ["💡 Идеи товаров"],
        ["📂 Мои запросы"],
        ["❓ Как это работает", "💼 Тарифы"],
    ],
    resize_keyboard=True
)

# --- START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 MarketBoost запущен!\n\nВыбери функцию 👇",
        reply_markup=menu
    )

# --- ПОКАЗАТЬ ЗАПРОСЫ ---
async def show_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in user_requests or len(user_requests[user_id]) == 0:
        await update.message.reply_text("У тебя пока нет сохранённых запросов.")
        return

    text = "📂 Твои последние запросы:\n\n"

    for i, req in enumerate(user_requests[user_id][-5:], 1):
        text += f"{i}. {req}\n"

    await update.message.reply_text(text)

# --- AI ОТВЕТ ---
async def ai_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_text = update.message.text

    # Сохраняем запрос
    if user_id not in user_requests:
        user_requests[user_id] = []

    user_requests[user_id].append(user_text)

    await update.message.reply_text("⏳ Анализирую...")

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "Ты эксперт по маркетплейсам Wildberries и Ozon. Даёшь практические советы продавцам."
                },
                {
                    "role": "user",
                    "content": user_text
                }
            ],
            temperature=0.7,
            max_tokens=800
        )

        answer = completion.choices[0].message.content

        await update.message.reply_text(answer)

    except Exception as e:
        await update.message.reply_text(f"Ошибка AI:\n{e}")

# --- ОБРАБОТКА КНОПОК ---
async def menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📂 Мои запросы":
        await show_requests(update, context)
    else:
        await ai_answer(update, context)

# --- MAIN ---
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_router))

    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
