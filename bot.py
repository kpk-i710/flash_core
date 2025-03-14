import requests
import logging

# Токен вашего бота
TOKEN = "8077102765:AAG6ynKTzAfrqeDl9B09pnjwy0A-vwISuKs"

# Фиксированный chat_id
CHAT_ID = 1014623291

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_telegram_message(text):
    """
    Отправляет сообщение в Telegram.

    :param text: Текст сообщения.
    :return: True, если сообщение отправлено успешно, иначе False.
    """
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {
        "chat_id": CHAT_ID,  # Используем фиксированный chat_id
        "text": text
    }

    try:
        response = requests.get(url, params=params).json()
        if response.get("ok"):
            logger.info(f"Сообщение отправлено успешно! Текст: {text}")
            return True
        else:
            logger.error(f"Ошибка при отправке сообщения: {response}")
            return False
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        return False