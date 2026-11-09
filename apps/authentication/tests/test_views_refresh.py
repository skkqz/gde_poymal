from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

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

    def test_refresh_204(self):
        """
        Успешное обновление: старый refresh валиден, новый access
        возвращается только в cookie, тела ответа нет.
        """

        self.client.cookies[self.cookie_name] = str(self.refresh)

        response = self.client.post(reverse('token-refresh'), format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)
        self.assertIn('access_token', response.cookies)
        self.assertIn(self.cookie_name, response.cookies)

    def test_refresh_sets_httponly_access_cookie(self):
        """
        Access-cookie должна быть HttpOnly и session-cookie.
        """

        self.client.cookies[self.cookie_name] = str(self.refresh)

        response = self.client.post(reverse('token-refresh'), format='json')

        self.assertIn('access_token', response.cookies)
        cookie = response.cookies['access_token']
        self.assertTrue(cookie['httponly'])
        self.assertEqual(cookie['path'], '/api/')
        self.assertFalse(cookie.get('max-age'))
        self.assertFalse(cookie.get('expires'))

        token = AccessToken(cookie.value)
        self.assertEqual(str(token['user_id']), str(self.user.pk))

    def test_refresh_sets_httponly_access_cookie(self):
        """
        Access-cookie должна быть HttpOnly и session-cookie.
        """

        self.client.cookies[self.cookie_name] = str(self.refresh)

        response = self.client.post(reverse('token-refresh'), format='json')

        self.assertIn('access_token', response.cookies)
        cookie = response.cookies['access_token']
        self.assertTrue(cookie['httponly'])
        self.assertEqual(cookie['path'], '/api/')
        self.assertFalse(cookie.get('max-age'))
        self.assertFalse(cookie.get('expires'))

        token = AccessToken(cookie.value)
        self.assertEqual(str(token['user_id']), str(self.user.pk))

    def test_refresh_no_new_refresh_cookie(self):
        """
        Так как ROTATE_REFRESH_TOKENS=False, refresh-cookie не
        перевыпускается и не меняется.
        """

        self.client.cookies[self.cookie_name] = str(self.refresh)

        response = self.client.post(reverse('token-refresh'), format='json')

        self.assertEqual(
            response.cookies[self.cookie_name].value,
            str(self.refresh),
        )

    def test_refresh_requires_csrf(self):
        """
        Refresh требует CSRF: без X-CSRFToken отклоняется.
        """

        client = APIClient(enforce_csrf_checks=True)
        client.cookies[self.cookie_name] = str(self.refresh)

        response = client.post(
            reverse('token-refresh'),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_refresh_with_csrf_204(self):
        """
        Refresh с валидным X-CSRFToken проходит и обновляет access.
        """

        client = APIClient(enforce_csrf_checks=True)
        client.cookies[self.cookie_name] = str(self.refresh)
        client.get(reverse('csrf'))
        csrf_token = client.cookies['csrftoken'].value

        response = client.post(
            reverse('token-refresh'),
            format='json',
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIn('access_token', response.cookies)

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

    def test_refresh_remember_false(self):
        """
        При remember=false в query хедере refresh-cookie остаётся session.
        """

        self.client.cookies[self.cookie_name] = str(self.refresh)

        response = self.client.post(
            reverse('token-refresh'),
            format='json',
            data={'remember': False},
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        cookie = response.cookies[self.cookie_name]
        self.assertIsNone(cookie.get('max-age'))
        self.assertIsNone(cookie.get('expires'))

    def test_refresh_remember_true(self):
        """
        При remember=true в query хедере refresh-cookie становится
        persistent на 7 дней.
        """

        self.client.cookies[self.cookie_name] = str(self.refresh)

        response = self.client.post(
            reverse('token-refresh'),
            format='json',
            data={'remember': True},
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        cookie = response.cookies[self.cookie_name]
        self.assertIsNotNone(cookie.get('max-age'))
        self.assertIsNotNone(cookie.get('expires'))
