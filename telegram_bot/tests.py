from datetime import time, timedelta
from unittest.mock import patch

from django.test import TestCase, override_settings
from django.utils import timezone

from habits.models import Habit
from telegram_bot.services import send_telegram_message
from telegram_bot.tasks import build_reminder_message, send_habit_reminders
from users.models import User


class SendTelegramMessageTestCase(TestCase):
    """Тесты сервиса отправки сообщений."""

    @override_settings(TELEGRAM_BOT_TOKEN="TEST_TOKEN")
    @patch("telegram_bot.services.requests.post")
    def test_send_message_calls_telegram_api(self, mock_post):
        send_telegram_message("123456", "Тестовое сообщение")
        mock_post.assert_called_once_with(
            "https://api.telegram.org/botTEST_TOKEN/sendMessage",
            data={"chat_id": "123456", "text": "Тестовое сообщение"},
            timeout=10,
        )


class BuildReminderMessageTestCase(TestCase):
    def test_message_contains_related_habit(self):
        user = User.objects.create_user(email="u@example.com", password="Str0ngPass!")
        pleasant = Habit.objects.create(
            user=user,
            place="Дом",
            time=time(22, 0),
            action="ванна с пеной",
            is_pleasant=True,
            execution_time=100,
        )
        useful = Habit.objects.create(
            user=user,
            place="Улица",
            time=time(20, 0),
            action="прогулка",
            execution_time=120,
            related_habit=pleasant,
        )
        message = build_reminder_message(useful)
        self.assertIn("прогулка", message)
        self.assertIn("ванна с пеной", message)


class HabitRemindersTaskTestCase(TestCase):
    """Тесты Celery-задачи напоминаний."""

    def setUp(self):
        self.now = timezone.localtime().replace(second=0, microsecond=0)
        self.user = User.objects.create_user(email="tg@example.com", password="Str0ngPass!", telegram_chat_id="123456")

    def _create_habit(self, **extra):
        data = {
            "user": self.user,
            "place": "Парк",
            "time": self.now.time(),
            "action": "прогулка вокруг квартала",
            "execution_time": 90,
        }
        data.update(extra)
        return Habit.objects.create(**data)

    def _run_task(self):
        with patch("telegram_bot.tasks.send_telegram_message") as mock_send, patch(
            "telegram_bot.tasks.timezone.now", return_value=self.now
        ):
            send_habit_reminders()
        return mock_send

    def test_reminder_sent_for_matching_time(self):
        self._create_habit()
        mock_send = self._run_task()
        mock_send.assert_called_once()
        chat_id, message = mock_send.call_args[0]
        self.assertEqual(chat_id, "123456")
        self.assertIn("прогулка вокруг квартала", message)

    def test_reminder_not_sent_for_other_time(self):
        self._create_habit(time=(self.now + timedelta(hours=1)).time())
        self._run_task().assert_not_called()

    def test_reminder_not_sent_without_linked_telegram(self):
        self.user.telegram_chat_id = None
        self.user.save(update_fields=["telegram_chat_id"])
        self._create_habit()
        self._run_task().assert_not_called()

    def test_reminder_respects_periodicity(self):
        habit = self._create_habit(periodicity=7)
        Habit.objects.filter(pk=habit.pk).update(created_at=self.now - timedelta(days=3))
        self._run_task().assert_not_called()

        Habit.objects.filter(pk=habit.pk).update(created_at=self.now - timedelta(days=7))
        self._run_task().assert_called_once()

    def test_message_contains_reward(self):
        self._create_habit(reward="чашка кофе")
        mock_send = self._run_task()
        self.assertIn("чашка кофе", mock_send.call_args[0][1])
