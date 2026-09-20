"""Тесты LogoutView и MeView."""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import CustomUser


class LogoutViewTest(APITestCase):
    """Тесты LogoutView."""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='StrongPass123',
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.access = str(self.refresh.access_token)

    def test_logout_204(self):
        """
        Успешный выход.

        :return: None
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')
        data = {'refresh': str(self.refresh)}
        response = self.client.post(reverse('logout'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_logout_invalid_refresh_400(self):
        """
        Неверный refresh токен должен возвращать 400.

        :return: None
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')
        data = {'refresh': 'invalid_token'}
        response = self.client.post(reverse('logout'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_other_user_refresh_400(self):
        """
        Refresh токен другого пользователя должен возвращать 400.

        :return: None
        """
        other_user = CustomUser.objects.create_user(
            email='other@example.com',
            password='StrongPass123',
        )
        other_refresh = RefreshToken.for_user(other_user)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')
        data = {'refresh': str(other_refresh)}
        response = self.client.post(reverse('logout'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_without_auth_401(self):
        """
        Выход без токена должен возвращать 401.

        :return: None
        """
        data = {'refresh': 'some_token'}
        response = self.client.post(reverse('logout'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_refresh_blacklisted(self):
        """
        После выхода refresh токен должен быть в blacklist.

        :return: None
        """
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')
        data = {'refresh': str(self.refresh)}
        self.client.post(reverse('logout'), data, format='json')

        # Пытаемся использовать заблокированный токен для refresh
        from rest_framework_simplejwt.views import TokenRefreshView
        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        request = factory.post('/api/auth/refresh/', {'refresh': str(self.refresh)}, format='json')
        view = TokenRefreshView.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)