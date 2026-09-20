"""Тесты представлений аутентификации."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import CustomUser


class RegisterViewTest(APITestCase):
    """Тесты RegisterView."""

    def test_register_201(self):
        """
        Успешная регистрация.

        :return: None
        """
        data = {
            'email': 'new@example.com',
            'password': 'StrongPass123',
            'password2': 'StrongPass123',
        }
        response = self.client.post(reverse('register'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertEqual(response.data['email'], 'new@example.com')
        self.assertNotIn('password', response.data)

    def test_register_duplicate_email_400(self):
        """
        Регистрация с существующим email должна возвращать 400.

        :return: None
        """
        # Создаем пользователя
        CustomUser.objects.create_user(
            email='existing@example.com',
            password='StrongPass123',
        )
        data = {
            'email': 'existing@example.com',
            'password': 'StrongPass123',
            'password2': 'StrongPass123',
        }
        response = self.client.post(reverse('register'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('уже существует', str(response.data))

    def test_register_password_mismatch_400(self):
        """
        Несовпадение паролей должно возвращать 400.

        :return: None
        """
        data = {
            'email': 'new@example.com',
            'password': 'StrongPass123',
            'password2': 'DifferentPass123',
        }
        response = self.client.post(reverse('register'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('не совпадают', str(response.data))

    def test_register_short_password_400(self):
        """
        Короткий пароль должен возвращать 400.

        :return: None
        """
        data = {
            'email': 'test@example.com',
            'password': '123',
            'password2': '123',
        }
        response = self.client.post(reverse('register'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_email_normalized(self):
        """
        Email должен нормализоваться к нижнему регистру.

        :return: None
        """
        data = {
            'email': 'User@EXAMPLE.COM',
            'password': 'StrongPass123',
            'password2': 'StrongPass123',
        }
        response = self.client.post(reverse('register'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], 'user@example.com')