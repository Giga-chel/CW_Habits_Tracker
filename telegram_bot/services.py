import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def send_telegram_message(chat_id, text):
    """Отправляет сообщение пользователю через Telegram Bot API."""
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(url, data={"chat_id": chat_id, "text": text}, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        logger.exception("Не удалось отправить сообщение в Telegram (chat_id=%s)", chat_id)
        return False
    return True
