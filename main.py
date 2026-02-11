import os
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================
# TOKENS
# =========================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
QWEN_API_KEY = os.getenv("QWEN_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("Нет TELEGRAM_TOKEN")

if not QWEN_API_KEY:
    raise ValueError("Нет QWEN_API_KEY")

print("Бот запущен...")

# =========================
# MEMORY
# =========================

user_requests = {}

# =========================
# MENU
# =========================

menu = ReplyKeyboardMarkup(
    [
        ["📦 Анализ товара", "💰 Юнит-экономика"],
        ["📈 Продвижение", "🛍 Улучшить карточку"],
        ["🧠 Мои запросы", "📰 Новости маркетплейсов"],
        ["ℹ️ Как это работает"],
    ],
    resize_keyboard=True,
)

# =========================
# AI REQUEST
# =========================

def ask_qwen(prompt: str) -> str:
    url = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {QWEN_API_KEY.strip()}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "qwen-plus",
        "messages": [
            {
                "role": "system",
                "content": "Ты эксперт по торговле на маркетплейсах Wildberries, Ozon и Amazon.",
            },
            {"role": "user", "content": prompt},
        ],
    }

    response = requests.post(url, headers=headers, json=data)

    result = response.json()

    return result["choices"][0]["message"]["content"]

# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 MarketBoost запущен!\n\nВыбери инструмент:",
        reply_markup=menu,
    )

# =========================
# BUTTON HANDLER
# =========================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id

    await update.message.reply_text("⏳ Анализирую...")

    if text == "ℹ️ Как это работает":
        await update.message.reply_text(
            "Я анализирую товары, считаю прибыль, помогаю с продвижением "
            "и улучшаю карточки товаров с помощью AI."
        )
        return

    prompt = text

    try:
        answer = ask_qwen(prompt)

        # memory
        user_requests.setdefault(user_id, []).append(prompt)

        await update.message.reply_text(answer)

    except Exception as e:
        await update.message.reply_text("❌ Ошибка AI. Попробуй позже.")
        print(e)

# =========================
# MY REQUESTS
# =========================

async def my_requests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    history = user_requests.get(user_id, [])

    if not history:
        await update.message.reply_text("Запросов пока нет.")
        return

    text = "\n".join(history[-5:])

    await update.message.reply_text(f"🧠 Последние запросы:\n\n{text}")

# =========================
# MAIN
# =========================

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(
        MessageHandler(filters.Regex("🧠 Мои запросы"), my_requests)
    )

    app.run_polling()

if __name__ == "__main__":
    main()
