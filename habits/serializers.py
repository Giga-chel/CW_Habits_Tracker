from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from habits.models import Habit
from habits.validators import validate_execution_time, validate_periodicity


class HabitSerializer(ModelSerializer):
    """Сериализатор привычки с валидацией бизнес-правил."""

    class Meta:
        model = Habit
        fields = "__all__"
        read_only_fields = ("user", "created_at")

    def validate_execution_time(self, value):
        return validate_execution_time(value)

    def validate_periodicity(self, value):
        return validate_periodicity(value)

    def validate(self, attrs):
        is_pleasant = self._current_value(attrs, "is_pleasant") or False
        reward = self._current_value(attrs, "reward")
        related_habit = self._current_value(attrs, "related_habit")

        # В связанные привычки попадают только приятные привычки
        if related_habit is not None and not related_habit.is_pleasant:
            raise ValidationError("В связанные привычки можно указывать только приятные привычки.")

        # Исключаем одновременный выбор связанной привычки и вознаграждения
        if reward and related_habit is not None:
            raise ValidationError(
                "Нельзя одновременно указать связанную привычку и вознаграждение. Выберите что-то одно."
            )

        # У приятной привычки не может быть вознаграждения или связанной привычки
        if is_pleasant and (reward or related_habit is not None):
            raise ValidationError("У приятной привычки не может быть вознаграждения или связанной привычки.")

        # Связанная привычка должна принадлежать текущему пользователю
        request = self.context.get("request")
        if related_habit is not None and request is not None and related_habit.user != request.user:
            raise ValidationError("Связанной привычкой может быть только собственная привычка.")

        return attrs

    def _current_value(self, attrs, field_name):
        """Значение поля с учётом частичного обновления (PATCH)."""
        if field_name in attrs:
            return attrs[field_name]
        if self.instance is not None:
            return getattr(self.instance, field_name)
        return None


class PublicHabitSerializer(HabitSerializer):
    """Сериализатор публичных привычек (без приватных данных)."""

    class Meta(HabitSerializer.Meta):
        fields = (
            "id",
            "place",
            "time",
            "action",
            "is_pleasant",
            "periodicity",
            "execution_time",
            "reward",
            "is_public",
        )
