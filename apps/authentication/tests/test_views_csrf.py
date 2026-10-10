from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import CustomUser


@override_settings(CSRF_COOKIE_SECURE=False, CSRF_COOKIE_SAMESITE='Lax')
class CSRFTokenViewTest(APITestCase):
    """Тесты выдачи CSRF-cookie и CSRF-защиты cookie-authenticated эндпоинтов."""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='StrongPass123',
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.access = str(self.refresh.access_token)

    def test_csrf_endpoint_sets_cookie(self):
        """
        Bootstrap-эндпоинт должен устанавливать читаемую из JS csrftoken cookie.
        """

        response = self.client.get(reverse('csrf'))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIn('csrftoken', response.cookies)
        # CSRF_COOKIE_HTTPONLY = False: значение должно быть доступно document.cookie.
        self.assertFalse(response.cookies['csrftoken'].get('httponly'))

    def test_cookie_authenticated_post_without_csrf_token_403(self):
        """
        Logout без заголовка X-CSRFToken должен отклоняться middleware.
        """

        client = APIClient(enforce_csrf_checks=True)
        client.cookies['refresh_token'] = str(self.refresh)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')

        response = client.post(reverse('logout'), format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cookie_authenticated_post_with_csrf_token_204(self):
        """
        Logout с валидным CSRF-токеном должен проходить.
        """

        client = APIClient(enforce_csrf_checks=True)
        client.get(reverse('csrf'))
        csrf_token = client.cookies['csrftoken'].value

        client.cookies['refresh_token'] = str(self.refresh)
        client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access}',
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        response = client.post(reverse('logout'), format='json')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_login_and_register_not_csrf_protected(self):
        """
        Login и Register остаются csrf_exempt: cookie на момент вызова
        ещё не выдана, а первый запрос клиента не должен падать с 403.
        """

        cases = (
            (
                'login',
                {
                    'email': 'test@example.com',
                    'password': 'StrongPass123',
                },
                status.HTTP_200_OK,
            ),
            (
                'register',
                {
                    'email': 'new@example.com',
                    'password': 'StrongPass123',
                    'password2': 'StrongPass123',
                },
                status.HTTP_201_CREATED,
            ),
        )

        for url_name, payload, expected_status in cases:
            with self.subTest(url_name=url_name):
                client = APIClient(enforce_csrf_checks=True)
                response = client.post(reverse(url_name), payload, format='json')
                self.assertEqual(response.status_code, expected_status)
