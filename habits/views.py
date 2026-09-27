from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated

from habits.models import Habit
from habits.permissions import IsOwner
from habits.serializers import HabitSerializer, PublicHabitSerializer


class HabitCreateAPIView(CreateAPIView):
    """Создание привычки. Пользователь проставляется автоматически."""

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class HabitListAPIView(ListAPIView):
    """Список привычек текущего пользователя (пагинация по 5 штук)."""

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user)


class HabitPublicListAPIView(ListAPIView):
    """Список публичных привычек (только чтение)."""

    serializer_class = PublicHabitSerializer
    permission_classes = [IsAuthenticated]
    queryset = Habit.objects.filter(is_public=True)


class HabitRetrieveAPIView(RetrieveAPIView):
    """Просмотр своей привычки."""

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    queryset = Habit.objects.all()


class HabitUpdateAPIView(UpdateAPIView):
    """Редактирование своей привычки."""

    serializer_class = HabitSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    queryset = Habit.objects.all()


class HabitDestroyAPIView(DestroyAPIView):
    """Удаление своей привычки."""

    permission_classes = [IsAuthenticated, IsOwner]
    queryset = Habit.objects.all()
