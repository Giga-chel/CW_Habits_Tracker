from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class UserAPITestCase(APITestCase):
    """Тесты регистрации и авторизации."""

    def setUp(self):
        self.register_url = reverse("users:register")
        self.login_url = reverse("users:login")

    def test_registration(self):
        response = self.client.post(self.register_url, {"email": "new@example.com", "password": "Str0ngPass!"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="new@example.com").exists())
        self.assertNotIn("password", response.data)

    def test_registration_duplicate_email(self):
        User.objects.create_user(email="new@example.com", password="Str0ngPass!")
        response = self.client.post(self.register_url, {"email": "new@example.com", "password": "Str0ngPass!"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_weak_password(self):
        response = self.client.post(self.register_url, {"email": "weak@example.com", "password": "123"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_returns_tokens(self):
        User.objects.create_user(email="user@example.com", password="Str0ngPass!")
        response = self.client.post(self.login_url, {"email": "user@example.com", "password": "Str0ngPass!"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_wrong_password(self):
        User.objects.create_user(email="user@example.com", password="Str0ngPass!")
        response = self.client.post(self.login_url, {"email": "user@example.com", "password": "WrongPass!"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
