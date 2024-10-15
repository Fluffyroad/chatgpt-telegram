import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import openai

# Включаем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

logger.info("Запуск бота...")

# Настраиваем API ключи
TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # URL для вебхука

if not TELEGRAM_API_KEY or not OPENAI_API_KEY or not WEBHOOK_URL:
    logger.error("Не заданы TELEGRAM_API_KEY, OPENAI_API_KEY или WEBHOOK_URL. Проверь переменные окружения.")
    exit(1)

openai.api_key = OPENAI_API_KEY

async def start(update: Update, context) -> None:
    logger.info("Команда /start получена")
    await update.message.reply_text("Привет! Я бот, использующий ChatGPT.")

async def handle_message(update: Update, context) -> None:
    user_message = update.message.text
    logger.info(f"Получено сообщение от пользователя: {user_message}")
    
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # можно выбрать любой другой подходящий движок
            prompt=user_message,
            max_tokens=150
        )
        reply_text = response.choices[0].text.strip()
        logger.info(f"Ответ ChatGPT: {reply_text}")
        await update.message.reply_text(reply_text)
    except Exception as e:
        logger.error(f"Ошибка при запросе к OpenAI: {e}")
        await update.message.reply_text("Произошла ошибка при обработке запроса. Пожалуйста, попробуйте позже.")

async def help_command(update: Update, context) -> None:
    await update.message.reply_text("Напишите любое сообщение, и я отвечу вам с помощью ChatGPT!")

def main():
    """Запуск бота."""
    logger.info("Бот запускается с токеном Telegram")

    # Создаем приложение
    application = Application.builder().token(TELEGRAM_API_KEY).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Настройка вебхуков
    logger.info("Установка вебхука на URL")
    application.run_webhook(
        listen="0.0.0.0",  # сервер будет слушать все доступные IP-адреса
        port=int(os.environ.get("PORT", 5000)),  # получаем порт из окружения
        webhook_url=WEBHOOK_URL  # URL для вебхуков
    )

if __name__ == '__main__':
    main()
