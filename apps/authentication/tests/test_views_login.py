"""Тесты представлений аутентификации (продолжение)."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import CustomUser


class LoginViewTest(APITestCase):
    """Тесты LoginView."""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='StrongPass123',
        )

    def test_login_200(self):
        """
        Успешный вход.

        :return: None
        """
        data = {
            'email': 'test@example.com',
            'password': 'StrongPass123',
        }
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_wrong_password_400(self):
        """
        Неверный пароль должен возвращать 400 (ошибка валидации).

        :return: None
        """
        data = {
            'email': 'test@example.com',
            'password': 'WrongPass123',
        }
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Не верная', str(response.data))

    def test_login_nonexistent_user_400(self):
        """
        Несуществующий пользователь должен возвращать 400.

        :return: None
        """
        data = {
            'email': 'nonexistent@example.com',
            'password': 'StrongPass123',
        }
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_case_insensitive(self):
        """
        Вход должен быть нечувствителен к регистру email.

        :return: None
        """
        data = {
            'email': 'TEST@EXAMPLE.COM',
            'password': 'StrongPass123',
        }
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)