from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import CustomUser


class CookieTokenRefreshViewTest(APITestCase):
    """Тесты обновления access-токена по HttpOnly cookie."""

    cookie_name = 'refresh_token'

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='StrongPass123',
        )
        self.refresh = RefreshToken.for_user(self.user)

    def test_refresh_200(self):
        """
        Успешное обновление: новый access в теле, новый refresh в cookie.
        """

        self.client.cookies[self.cookie_name] = str(self.refresh)

        response = self.client.post(reverse('token-refresh'), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertNotIn('refresh', response.data)
        self.assertIn(self.cookie_name, response.cookies)
        self.assertNotEqual(response.cookies[self.cookie_name].value, str(self.refresh))

    def test_refresh_rotates_and_blacklists_old_token(self):
        """
        Старый refresh должен попасть в blacklist, новый — быть валидным.
        """

        self.client.cookies[self.cookie_name] = str(self.refresh)

        response = self.client.post(reverse('token-refresh'), format='json')

        new_refresh = response.cookies[self.cookie_name].value

        with self.assertRaises(TokenError):
            RefreshToken(str(self.refresh))

        self.assertEqual(str(RefreshToken(new_refresh)['user_id']), str(self.user.pk))

    def test_refresh_without_cookie_401(self):
        """
        Отсутствие refresh-cookie должно возвращать 401 без новой cookie.
        """

        response = self.client.post(reverse('token-refresh'), format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn(self.cookie_name, response.cookies)

    def test_refresh_invalid_cookie_401(self):
        """
        Некорректный refresh в cookie должен возвращать 401.
        """

        self.client.cookies[self.cookie_name] = 'invalid_token'

        response = self.client.post(reverse('token-refresh'), format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_blacklisted_cookie_401(self):
        """
        Забаненный refresh не должен обновлять access-токен.
        """

        self.refresh.blacklist()
        self.client.cookies[self.cookie_name] = str(self.refresh)

        response = self.client.post(reverse('token-refresh'), format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
