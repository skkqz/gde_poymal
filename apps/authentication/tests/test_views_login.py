from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from apps.users.models import CustomUser


class LoginViewTest(APITestCase):
    """Тесты LoginView."""

    access_cookie_name = 'access_token'
    refresh_cookie_name = 'refresh_token'

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='StrongPass123',
        )

    def test_login_200(self):
        """
        Успешный вход: токены только в cookie, в теле — пользователь.
        """

        data = {
            'email': 'test@example.com',
            'password': 'StrongPass123',
        }
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('access', response.data)
        self.assertIn('user', response.data)
        self.assertNotIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], self.user.email)

    def test_login_sets_httponly_access_cookie(self):
        """
        Access-токен должен устанавливаться в session HttpOnly cookie.
        """

        data = {
            'email': 'test@example.com',
            'password': 'StrongPass123',
        }
        response = self.client.post(reverse('login'), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.access_cookie_name, response.cookies)

        cookie = response.cookies[self.access_cookie_name]
        self.assertTrue(cookie['httponly'])
        self.assertEqual(cookie['path'], '/api/')
        self.assertEqual(cookie['samesite'], 'Lax')
        self.assertFalse(cookie.get('max-age'))
        self.assertFalse(cookie.get('expires'))

        token = AccessToken(cookie.value)
        self.assertEqual(str(token['user_id']), str(self.user.pk))

    def test_login_sets_httponly_refresh_cookie(self):
        """
        Refresh-токен должен устанавливаться в защищённую HttpOnly cookie.
        """

        data = {
            'email': 'test@example.com',
            'password': 'StrongPass123',
        }
        response = self.client.post(reverse('login'), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.refresh_cookie_name, response.cookies)

        cookie = response.cookies[self.refresh_cookie_name]
        self.assertTrue(cookie['httponly'])
        self.assertEqual(cookie['path'], '/api/auth/')
        self.assertEqual(cookie['samesite'], 'Lax')

        token = RefreshToken(cookie.value)
        self.assertEqual(str(token['user_id']), str(self.user.pk))

    def test_login_wrong_password_400(self):
        """
        Неверный пароль должен возвращать 400 (ошибка валидации).
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
        """

        data = {
            'email': 'TEST@EXAMPLE.COM',
            'password': 'StrongPass123',
        }
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['email'], 'test@example.com')
