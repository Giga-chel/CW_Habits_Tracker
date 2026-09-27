from rest_framework.exceptions import ValidationError


def validate_execution_time(value):
    """Время выполнения — не больше 120 секунд."""
    if value > 120:
        raise ValidationError("Время выполнения привычки не может превышать 120 секунд.")
    return value


def validate_periodicity(value):
    """Нельзя выполнять привычку реже одного раза в 7 дней."""
    if value < 1 or value > 7:
        raise ValidationError("Периодичность выполнения привычки — от 1 до 7 дней.")
    return value
