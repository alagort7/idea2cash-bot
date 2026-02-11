import os
import requests
import logging

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================
# ЛОГИ
# =========================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# =========================
# API KEYS
# =========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
QWEN_API_KEY = os.getenv("QWEN_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("Нет TELEGRAM_TOKEN")

if not QWEN_API_KEY:
    raise ValueError("Нет QWEN_API_KEY")


# =========================
# КНОПКИ
# =========================
keyboard = [
    ["📦 Анализ товара", "💰 Юнит-экономика"],
    ["📈 Продвижение", "🧠 Мои запросы"],
    ["📰 Новости маркетплейсов"],
]

markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# =========================
# QWEN ЗАПРОС
# =========================
def ask_qwen(prompt):

    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {QWEN_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "qwen3-max",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Ты эксперт по маркетплейсам (Wildberries, Ozon, Amazon). "
                    "Даешь прикладные советы продавцам."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 800,
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        return f"Ошибка API: {response.text}"

    result = response.json()

    return result["choices"][0]["message"]["content"]


# =========================
# START
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "MarketBoost AI запущен. Выберите раздел:",
        reply_markup=markup,
    )


# =========================
# HANDLE
# =========================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_text = update.message.text

    msg = await update.message.reply_text("Анализирую...")

    try:

        answer = ask_qwen(user_text)

        await msg.edit_text(answer)

    except Exception as e:

        logging.error(e)

        await msg.edit_text(f"Ошибка: {e}")


# =========================
# APP
# =========================
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("Бот запущен...")

app.run_polling()
