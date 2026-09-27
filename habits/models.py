from django.conf import settings
from django.db import models


class Habit(models.Model):
    """Полезная или приятная привычка пользователя."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="habits",
        verbose_name="Пользователь",
        help_text="Создатель привычки",
    )
    place = models.CharField(max_length=100, verbose_name="Место", help_text="Место выполнения привычки")
    time = models.TimeField(verbose_name="Время", help_text="Время, когда необходимо выполнять привычку")
    action = models.CharField(max_length=200, verbose_name="Действие", help_text="Действие привычки")
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name="Признак приятной привычки",
        help_text="Приятная привычка — способ вознаградить себя за полезную",
    )
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="useful_habits",
        limit_choices_to={"is_pleasant": True},
        verbose_name="Связанная привычка",
        help_text="Приятная привычка, привязанная к полезной",
    )
    periodicity = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Периодичность",
        help_text="Периодичность выполнения в днях (1–7, по умолчанию ежедневно)",
    )
    reward = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Вознаграждение",
        help_text="Чем вознаградить себя после выполнения",
    )
    execution_time = models.PositiveSmallIntegerField(
        verbose_name="Время на выполнение",
        help_text="Время выполнения в секундах (не более 120)",
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name="Признак публичности",
        help_text="Доступна ли привычка другим пользователям",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
        help_text="Точка отсчёта расписания напоминаний",
    )

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ("id",)

    def __str__(self):
        return f"Я буду {self.action} в {self.time} в {self.place}"
