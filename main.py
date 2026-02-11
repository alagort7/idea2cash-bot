import os
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# =========================
# API KEYS
# =========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
QWEN_API_KEY = os.getenv("QWEN_API_KEY")

# =========================
# КНОПКИ
# =========================
keyboard = [
    ["📦 Анализ товара", "💰 Юнит-экономика"],
    ["📈 Продвижение", "🧠 Мои запросы"],
    ["📰 Новости маркетплейсов"]
]

markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# =========================
# QWEN AI ЗАПРОС
# =========================
def ask_qwen(prompt):

    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {QWEN_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "qwen3-max",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Ты эксперт по торговле на маркетплейсах "
                    "(Wildberries, Ozon, Amazon). "
                    "Даешь практические, прикладные советы продавцам."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 900
    }

    response = requests.post(url, headers=headers, json=data)

    result = response.json()

    return result["choices"][0]["message"]["content"]


# =========================
# /start
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "AI-ассистент продавца маркетплейсов запущен.",
        reply_markup=markup
    )


# =========================
# ОБРАБОТКА СООБЩЕНИЙ
# =========================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_text = update.message.text

    msg = await update.message.reply_text("Анализирую...")

    try:

        answer = ask_qwen(user_text)

        await msg.edit_text(answer)

    except Exception as e:

        await msg.edit_text(f"Ошибка AI: {e}")


# =========================
# ЗАПУСК
# =========================
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

app.run_polling()
