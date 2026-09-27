from django.urls import path

from habits.views import (
    HabitCreateAPIView,
    HabitDestroyAPIView,
    HabitListAPIView,
    HabitPublicListAPIView,
    HabitRetrieveAPIView,
    HabitUpdateAPIView,
)

app_name = "habits"

urlpatterns = [
    path("", HabitListAPIView.as_view(), name="habit_list"),
    path("create/", HabitCreateAPIView.as_view(), name="habit_create"),
    path("public/", HabitPublicListAPIView.as_view(), name="habit_public_list"),
    path("<int:pk>/", HabitRetrieveAPIView.as_view(), name="habit_detail"),
    path("update/<int:pk>/", HabitUpdateAPIView.as_view(), name="habit_update"),
    path("delete/<int:pk>/", HabitDestroyAPIView.as_view(), name="habit_delete"),
]
