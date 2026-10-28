from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import CustomUser


@override_settings(CSRF_COOKIE_SECURE=False, CSRF_COOKIE_SAMESITE='Lax')
class CsrfProtectionTest(APITestCase):
    """Тесты CSRF-защиты публичных и cookie-аутентифицированных эндпоинтов."""

    access_cookie_name = 'access_token'
    refresh_cookie_name = 'refresh_token'

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='StrongPass123',
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.access = str(self.refresh.access_token)
        self.user_url = reverse('user_detail', kwargs={'pk': self.user.pk})

    def _client_with_csrf(self) -> APIClient:
        """
        Создать клиент с CSRF-проверкой и валидной csrftoken-cookie.

        :return: Тестовый API-клиент.
        """

        client = APIClient(enforce_csrf_checks=True)
        response = client.get(reverse('csrf'))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        return client

    @staticmethod
    def _csrf_token(client: APIClient) -> str:
        """
        Вернуть значение csrftoken из cookie клиента.

        :param client: Тестовый API-клиент.
        :return: Значение CSRF-токена.
        """

        return client.cookies['csrftoken'].value

    def test_csrf_endpoint_sets_readable_cookie(self):
        """Bootstrap-эндпоинт отдаёт csrftoken, читаемый из JavaScript."""

        response = self.client.get(reverse('csrf'))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIn('csrftoken', response.cookies)
        self.assertFalse(response.cookies['csrftoken'].get('httponly'))

    def test_login_without_csrf_403(self):
        """Login без X-CSRFToken отклоняется."""

        client = APIClient(enforce_csrf_checks=True)

        response = client.post(
            reverse('login'),
            {'email': self.user.email, 'password': 'StrongPass123'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_with_csrf_200(self):
        """Login с валидным X-CSRFToken проходит и ставит обе cookie."""

        client = self._client_with_csrf()

        response = client.post(
            reverse('login'),
            {'email': self.user.email, 'password': 'StrongPass123'},
            format='json',
            HTTP_X_CSRFTOKEN=self._csrf_token(client),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.access_cookie_name, response.cookies)
        self.assertIn(self.refresh_cookie_name, response.cookies)

    def test_register_without_csrf_403(self):
        """Register без X-CSRFToken отклоняется и не создаёт пользователя."""

        client = APIClient(enforce_csrf_checks=True)

        response = client.post(
            reverse('register'),
            {
                'email': 'new@example.com',
                'password': 'StrongPass123',
                'password2': 'StrongPass123',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(
            CustomUser.objects.filter(email='new@example.com').exists(),
        )

    def test_register_with_csrf_201(self):
        """Register с валидным X-CSRFToken проходит."""

        client = self._client_with_csrf()

        response = client.post(
            reverse('register'),
            {
                'email': 'new@example.com',
                'password': 'StrongPass123',
                'password2': 'StrongPass123',
            },
            format='json',
            HTTP_X_CSRFTOKEN=self._csrf_token(client),
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cookie_patch_without_csrf_403(self):
        """PATCH профиля по access-cookie без CSRF отклоняется."""

        client = APIClient(enforce_csrf_checks=True)
        client.cookies[self.access_cookie_name] = self.access

        response = client.patch(
            self.user_url,
            {'first_name': 'Иван'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.first_name, 'Иван')

    def test_cookie_patch_with_csrf_200(self):
        """PATCH профиля по access-cookie с CSRF проходит."""

        client = self._client_with_csrf()
        client.cookies[self.access_cookie_name] = self.access

        response = client.patch(
            self.user_url,
            {'first_name': 'Иван'},
            format='json',
            HTTP_X_CSRFTOKEN=self._csrf_token(client),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Иван')

    def test_bearer_patch_without_csrf_200(self):
        """PATCH с Bearer не требует CSRF."""

        client = APIClient(enforce_csrf_checks=True)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')

        response = client.patch(
            self.user_url,
            {'first_name': 'Иван'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Иван')

    def test_cookie_delete_without_csrf_403(self):
        """DELETE профиля по access-cookie без CSRF отклоняется."""

        client = APIClient(enforce_csrf_checks=True)
        client.cookies[self.access_cookie_name] = self.access

        response = client.delete(self.user_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(CustomUser.objects.filter(pk=self.user.pk).exists())

    def test_cookie_delete_with_csrf_204(self):
        """DELETE профиля по access-cookie с CSRF проходит."""

        client = self._client_with_csrf()
        client.cookies[self.access_cookie_name] = self.access

        response = client.delete(
            self.user_url,
            HTTP_X_CSRFTOKEN=self._csrf_token(client),
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CustomUser.objects.filter(pk=self.user.pk).exists())

    def test_cookie_password_change_without_csrf_403(self):
        """Смена пароля по access-cookie без CSRF отклоняется."""

        client = APIClient(enforce_csrf_checks=True)
        client.cookies[self.access_cookie_name] = self.access

        response = client.post(
            reverse('password_change'),
            {
                'old_password': 'StrongPass123',
                'new_password': 'AnotherPass123',
                'new_password2': 'AnotherPass123',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('StrongPass123'))

    def test_cookie_password_change_with_csrf_200(self):
        """Смена пароля по access-cookie с CSRF проходит."""

        client = self._client_with_csrf()
        client.cookies[self.access_cookie_name] = self.access

        response = client.post(
            reverse('password_change'),
            {
                'old_password': 'StrongPass123',
                'new_password': 'AnotherPass123',
                'new_password2': 'AnotherPass123',
            },
            format='json',
            HTTP_X_CSRFTOKEN=self._csrf_token(client),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('AnotherPass123'))

    def test_bearer_password_change_without_csrf_200(self):
        """Смена пароля с Bearer не требует CSRF."""

        client = APIClient(enforce_csrf_checks=True)
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')

        response = client.post(
            reverse('password_change'),
            {
                'old_password': 'StrongPass123',
                'new_password': 'AnotherPass123',
                'new_password2': 'AnotherPass123',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('AnotherPass123'))

    def test_logout_without_csrf_403(self):
        """Logout по cookie без CSRF отклоняется."""

        client = APIClient(enforce_csrf_checks=True)
        client.cookies[self.access_cookie_name] = self.access

        response = client.post(reverse('logout'), format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_logout_with_csrf_204(self):
        """Logout по cookie с CSRF проходит."""

        client = self._client_with_csrf()
        client.cookies[self.access_cookie_name] = self.access
        client.cookies[self.refresh_cookie_name] = str(self.refresh)

        response = client.post(
            reverse('logout'),
            format='json',
            HTTP_X_CSRFTOKEN=self._csrf_token(client),
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_password_reset_request_without_csrf_200(self):
        """Публичный запрос сброса пароля не требует CSRF."""

        client = APIClient(enforce_csrf_checks=True)

        response = client.post(
            reverse('password_reset_request'),
            {'email': self.user.email},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
