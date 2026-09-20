import logging

from celery import shared_task
from django.utils import timezone

from habits.models import Habit
from telegram_bot.services import send_telegram_message

logger = logging.getLogger(__name__)


def build_reminder_message(habit):
    """Формирует текст напоминания о привычке."""
    message = "Напоминание о привычке!\n\n" f"Я буду {habit.action} в {habit.time.strftime('%H:%M')} в {habit.place}."
    if habit.reward:
        message += f"\nВознаграждение после выполнения: {habit.reward}."
    if habit.related_habit_id:
        message += f"\nПриятная привычка после выполнения: {habit.related_habit.action}."
    return message


@shared_task
def send_habit_reminders():
    """Раз в минуту находит привычки, которые пора выполнять, и рассылает напоминания."""
    now = timezone.localtime(timezone.now())
    habits = Habit.objects.filter(
        user__telegram_chat_id__isnull=False,
        time__hour=now.hour,
        time__minute=now.minute,
    ).select_related("user", "related_habit")

    sent = 0
    for habit in habits:
        days_since_creation = (now.date() - timezone.localtime(habit.created_at).date()).days
        if days_since_creation % habit.periodicity != 0:
            continue
        if send_telegram_message(habit.user.telegram_chat_id, build_reminder_message(habit)):
            sent += 1

    logger.info("Отправлено напоминаний: %s", sent)
    return sent
