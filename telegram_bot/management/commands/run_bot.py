import logging

from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.management.base import BaseCommand
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from users.models import User

logger = logging.getLogger(__name__)

WAITING_FOR_EMAIL = 0


@sync_to_async
def link_chat_id(email, chat_id):
    """Привязывает chat_id к пользователю с указанным email."""
    user = User.objects.filter(email=email).first()
    if user is None:
        return False
    user.telegram_chat_id = str(chat_id)
    user.save(update_fields=["telegram_chat_id"])
    return True


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик /start: просит email для привязки аккаунта."""
    await update.effective_message.reply_text(
        "Привет! Это бот сервиса полезных привычек.\n" "Отправьте email вашего аккаунта, чтобы получать напоминания."
    )
    return WAITING_FOR_EMAIL


async def receive_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Получает email и привязывает Telegram-чат к аккаунту."""
    email = update.effective_message.text.strip()
    linked = await link_chat_id(email, update.effective_chat.id)
    if linked:
        await update.effective_message.reply_text(
            "Аккаунт привязан! Теперь я буду присылать вам напоминания о привычках."
        )
        return ConversationHandler.END
    await update.effective_message.reply_text(
        "Пользователь с таким email не найден. Проверьте email и попробуйте ещё раз."
    )
    return WAITING_FOR_EMAIL


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.effective_message.reply_text("Привязка отменена. /start — начать заново.")
    return ConversationHandler.END


class Command(BaseCommand):
    help = "Запуск Telegram-бота для привязки аккаунтов пользователей"

    def handle(self, *args, **options):
        application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        conversation = ConversationHandler(
            entry_points=[CommandHandler("start", start)],
            states={WAITING_FOR_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_email)]},
            fallbacks=[CommandHandler("cancel", cancel)],
        )
        application.add_handler(conversation)
        self.stdout.write(self.style.SUCCESS("Telegram-бот запущен"))
        application.run_polling(allowed_updates=Update.ALL_TYPES)
