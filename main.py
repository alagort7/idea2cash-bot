import os
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from groq import Groq

# --- TOKEN ---
BOT_TOKEN = os.getenv("BOT_TOKEN")

# --- GROQ ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# --- МЕНЮ ---
keyboard = [
    [KeyboardButton("📉 Почему нет продаж"), KeyboardButton("🛍 Улучшить карточку")],
    [KeyboardButton("📊 Анализ ниши"), KeyboardButton("💰 Расчёт прибыли")],
    [KeyboardButton("💡 Идеи товаров")],
    [KeyboardButton("❓ Как это работает"), KeyboardButton("💼 Тарифы")]
]

markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# --- AI ФУНКЦИЯ ---
def ask_ai(prompt):

    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "Ты эксперт по маркетплейсам (Wildberries, Ozon). Даёшь практические советы по продажам товаров."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7,
        max_tokens=800
    )

    return response.choices[0].message.content


# --- /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 MarketBoost запущен!\n\n"
        "Выбери функцию 👇",
        reply_markup=markup
    )


# --- ОБРАБОТКА КНОПОК ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    prompts = {

        "📉 Почему нет продаж":
        "Почему товар на маркетплейсе может не продаваться? Дай чек-лист причин.",

        "🛍 Улучшить карточку":
        "Как улучшить карточку товара на Wildberries/Ozon чтобы увеличить продажи?",

        "📊 Анализ ниши":
        "Как анализировать нишу на маркетплейсах перед запуском товара?",

        "💰 Расчёт прибыли":
        "Как посчитать чистую прибыль товара на маркетплейсе? Формула + пример.",

        "💡 Идеи товаров":
        "Предложи 5 прибыльных идей товаров для маркетплейсов с кратким анализом.",

        "❓ Как это работает":
        "Объясни как работает сервис анализа товаров MarketBoost для клиентов.",

        "💼 Тарифы":
        "Опиши тарифы сервиса анализа маркетплейсов: базовый, стандарт, премиум."
    }

    if text in prompts:

        await update.message.reply_text("⏳ Анализирую...")

        answer = ask_ai(prompts[text])

        await update.message.reply_text(answer)

    else:
        await update.message.reply_text(
            "Выбери кнопку из меню 👇",
            reply_markup=markup
        )


# --- MAIN ---
def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot started...")
    app.run_polling()


if __name__ == "__main__":
    main()
