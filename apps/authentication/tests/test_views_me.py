from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import CustomUser


class MeViewTest(APITestCase):
    """Тесты MeView."""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='StrongPass123',
            first_name='Ivan',
            last_name='Ivanov',
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.access = str(self.refresh.access_token)

    def test_me_200(self):
        """
        Успешное получение профиля.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')
        response = self.client.get(reverse('me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['first_name'], 'Ivan')
        self.assertEqual(response.data['last_name'], 'Ivanov')
        self.assertNotIn('password', response.data)

    def test_me_without_auth_401(self):
        """
        Без токена должен возвращать 401.
        """

        response = self.client.get(reverse('me'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_invalid_token_401(self):
        """
        Невалидный токен должен возвращать 401.
        """

        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        response = self.client.get(reverse('me'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
