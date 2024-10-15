import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import openai

# Включаем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

logger.info("Запуск бота...")

# Настраиваем API ключи
TELEGRAM_API_KEY = os.getenv("TELEGRAM_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_API_KEY or not OPENAI_API_KEY:
    logger.error("Не заданы TELEGRAM_API_KEY или OPENAI_API_KEY. Проверь переменные окружения.")
    exit(1)  # Завершаем программу, если ключи не заданы

openai.api_key = OPENAI_API_KEY

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Команда /start получена")
    await update.message.reply_text("Привет! Я бот, использующий ChatGPT.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    logger.info(f"Получено сообщение от пользователя: {user_message}")
    
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # или любой другой подходящий движок
            prompt=user_message,
            max_tokens=150
        )
        reply_text = response.choices[0].text.strip()
        logger.info(f"Ответ ChatGPT: {reply_text}")
        await update.message.reply_text(reply_text)
    except Exception as e:
        logger.error(f"Ошибка при запросе к OpenAI: {e}")
        await update.message.reply_text("Произошла ошибка при обработке запроса. Пожалуйста, попробуйте позже.")

if __name__ == '__main__':
    logger.info("Бот запускается с токеном Telegram")
    
    try:
        application = ApplicationBuilder().token(TELEGRAM_API_KEY).build()
    except Exception as e:
        logger.error(f"Ошибка при создании приложения Telegram: {e}")
        exit(1)
    
    # Проверим, что приложение успешно строится
    logger.info("Приложение собрано, добавление хендлеров")

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))  # повторное использование команды start для help
    application.add_handler(CommandHandler("message", handle_message))

    logger.info("Запуск поллинга...")
    try:
        application.run_polling()
    except Exception as e:
        logger.error(f"Ошибка во время работы поллинга: {e}")
