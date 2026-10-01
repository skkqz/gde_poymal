from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import CustomUser


class LogoutViewTest(APITestCase):
    """Тесты LogoutView с refresh-токеном в HttpOnly cookie."""

    cookie_name = 'refresh_token'

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='StrongPass123',
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.access = str(self.refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')

    def test_logout_204(self):
        """
        Успешный выход: cookie удаляется с клиента.
        """

        self.client.cookies[self.cookie_name] = str(self.refresh)

        response = self.client.post(reverse('logout'), format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.cookies[self.cookie_name].value, '')
        self.assertEqual(response.cookies[self.cookie_name]['max-age'], 0)
        self.assertEqual(response.cookies[self.cookie_name]['path'], '/api/auth/')

    def test_logout_blacklists_refresh_token(self):
        """
        После выхода refresh-токен должен попасть в blacklist.
        """

        self.client.cookies[self.cookie_name] = str(self.refresh)

        self.client.post(reverse('logout'), format='json')

        # RefreshToken при разборе строки проверяет blacklist и падает с TokenError.
        with self.assertRaises(TokenError):
            RefreshToken(str(self.refresh))

    def test_logout_without_cookie_204(self):
        """
        Выход без cookie должен завершаться успехом.
        """

        response = self.client.post(reverse('logout'), format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.cookies[self.cookie_name]['max-age'], 0)

    def test_logout_invalid_cookie_204(self):
        """
        Некорректный refresh в cookie игнорируется, logout завершается.

        Ошибка парсинга токена сейчас проглатывается в LogoutView,
        поэтому наружу отдаётся 204, а не 400.
        """

        self.client.cookies[self.cookie_name] = 'invalid_token'

        response = self.client.post(reverse('logout'), format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_logout_keeps_other_user_token_valid(self):
        """
        Refresh-токен другого пользователя из cookie не должен баниться.
        """

        other_user = CustomUser.objects.create_user(
            email='other@example.com',
            password='StrongPass123',
        )
        other_refresh = RefreshToken.for_user(other_user)

        self.client.cookies[self.cookie_name] = str(other_refresh)

        response = self.client.post(reverse('logout'), format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Токен остаётся валидным: разбор строки не падает и user_id чужой.
        token = RefreshToken(str(other_refresh))
        self.assertEqual(str(token['user_id']), str(other_user.pk))

    def test_logout_without_auth_401(self):
        """
        Выход без access-токена должен возвращать 401.
        """

        self.client.credentials()
        self.client.cookies[self.cookie_name] = str(self.refresh)

        response = self.client.post(reverse('logout'), format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
