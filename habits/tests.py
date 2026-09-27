from datetime import time

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import Habit
from users.models import User


class HabitCRUDAPITestCase(APITestCase):
    """Тесты CRUD, прав доступа, пагинации и валидаторов."""

    def setUp(self):
        self.owner = User.objects.create_user(email="owner@example.com", password="Str0ngPass!")
        self.stranger = User.objects.create_user(email="stranger@example.com", password="Str0ngPass!")
        self.client.force_authenticate(user=self.owner)
        self.pleasant_habit = Habit.objects.create(
            user=self.owner,
            place="Дом",
            time=time(21, 0),
            action="принять ванну с пеной",
            is_pleasant=True,
            execution_time=100,
        )

    @staticmethod
    def habit_data(**extra):
        data = {
            "place": "Офис",
            "time": "09:00",
            "action": "выпить стакан воды",
            "execution_time": 30,
            "periodicity": 1,
        }
        data.update(extra)
        return data

    def _foreign_habit(self):
        return Habit.objects.create(
            user=self.stranger, place="Дом", time=time(8, 0), action="зарядка", execution_time=60
        )

    # --- создание ---

    def test_create_habit_sets_owner(self):
        response = self.client.post(reverse("habits:habit_create"), self.habit_data())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.get(pk=response.data["id"]).user, self.owner)

    def test_create_habit_with_reward(self):
        response = self.client.post(reverse("habits:habit_create"), self.habit_data(reward="съесть десерт"))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_habit_with_related_pleasant_habit(self):
        response = self.client.post(
            reverse("habits:habit_create"), self.habit_data(related_habit=self.pleasant_habit.pk)
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # --- валидаторы ---

    def test_validator_reward_and_related_habit_together(self):
        response = self.client.post(
            reverse("habits:habit_create"),
            self.habit_data(reward="съесть десерт", related_habit=self.pleasant_habit.pk),
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validator_execution_time_over_120_seconds(self):
        response = self.client.post(reverse("habits:habit_create"), self.habit_data(execution_time=121))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validator_periodicity_more_than_7_days(self):
        response = self.client.post(reverse("habits:habit_create"), self.habit_data(periodicity=8))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validator_related_habit_must_be_pleasant(self):
        useful_habit = Habit.objects.create(
            user=self.owner,
            place="Офис",
            time=time(9, 0),
            action="выпить стакан воды",
            execution_time=30,
            reward="кофе",
        )
        response = self.client.post(reverse("habits:habit_create"), self.habit_data(related_habit=useful_habit.pk))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validator_pleasant_habit_without_reward_and_related(self):
        response_with_reward = self.client.post(
            reverse("habits:habit_create"), self.habit_data(is_pleasant=True, reward="конфета")
        )
        self.assertEqual(response_with_reward.status_code, status.HTTP_400_BAD_REQUEST)

        response_with_related = self.client.post(
            reverse("habits:habit_create"),
            self.habit_data(is_pleasant=True, related_habit=self.pleasant_habit.pk),
        )
        self.assertEqual(response_with_related.status_code, status.HTTP_400_BAD_REQUEST)

    # --- списки и пагинация ---

    def test_list_shows_only_own_habits(self):
        self._foreign_habit()
        Habit.objects.create(
            user=self.owner, place="Улица", time=time(7, 0), action="пробежка", execution_time=120
        )
        response = self.client.get(reverse("habits:habit_list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        actions = [habit["action"] for habit in response.data["results"]]
        self.assertIn("пробежка", actions)
        self.assertNotIn("зарядка", actions)

    def test_pagination_five_per_page(self):
        for i in range(7):
            Habit.objects.create(
                user=self.owner, place="Дом", time=time(7, 0), action=f"привычка {i}", execution_time=30
            )
        # 7 новых + 1 приятная из setUp = 8 привычек
        response = self.client.get(reverse("habits:habit_list"))
        self.assertEqual(response.data["count"], 8)
        self.assertEqual(len(response.data["results"]), 5)
        self.assertIsNotNone(response.data["next"])

        response = self.client.get(reverse("habits:habit_list"), {"offset": 5})
        self.assertEqual(len(response.data["results"]), 3)
        self.assertIsNone(response.data["next"])

    def test_public_habits_list(self):
        Habit.objects.create(
            user=self.stranger,
            place="Парк",
            time=time(8, 0),
            action="прогулка",
            execution_time=120,
            is_public=True,
        )
        Habit.objects.create(user=self.stranger, place="Дом", time=time(9, 0), action="медитация", execution_time=60)
        response = self.client.get(reverse("habits:habit_public_list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["action"], "прогулка")

    # --- права доступа ---

    def test_retrieve_own_habit(self):
        habit = Habit.objects.create(
            user=self.owner, place="Дом", time=time(8, 0), action="зарядка", execution_time=60
        )
        response = self.client.get(reverse("habits:habit_detail", args=[habit.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["action"], "зарядка")

    def test_update_own_habit(self):
        habit = Habit.objects.create(
            user=self.owner, place="Дом", time=time(8, 0), action="зарядка", execution_time=60, reward="кофе"
        )
        response = self.client.patch(reverse("habits:habit_update", args=[habit.pk]), {"action": "зарядка 10 минут"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        habit.refresh_from_db()
        self.assertEqual(habit.action, "зарядка 10 минут")

    def test_delete_own_habit(self):
        habit = Habit.objects.create(
            user=self.owner, place="Дом", time=time(8, 0), action="зарядка", execution_time=60
        )
        response = self.client.delete(reverse("habits:habit_delete", args=[habit.pk]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Habit.objects.filter(pk=habit.pk).exists())

    def test_stranger_cannot_update_foreign_habit(self):
        response = self.client.patch(
            reverse("habits:habit_update", args=[self._foreign_habit().pk]), {"action": "взлом"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_stranger_cannot_delete_foreign_habit(self):
        response = self.client.delete(reverse("habits:habit_delete", args=[self._foreign_habit().pk]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_request_denied(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse("habits:habit_list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
