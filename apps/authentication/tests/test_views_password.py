from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import CustomUser


class PasswordChangeViewTest(APITestCase):
    """Тесты PasswordChangeView."""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='OldPass123',
        )
        self.refresh = RefreshToken.for_user(self.user)
        self.access = str(self.refresh.access_token)

    def test_password_change_200(self):
        """
        Успешная смена пароля.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')
        data = {
            'old_password': 'OldPass123',
            'new_password': 'NewPass456',
            'new_password2': 'NewPass456',
        }
        response = self.client.post(reverse('password_change'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что новый пароль работает
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPass456'))

    def test_password_change_wrong_old_400(self):
        """
        Неверный старый пароль должен возвращать 400.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')
        data = {
            'old_password': 'WrongPass123',
            'new_password': 'NewPass456',
            'new_password2': 'NewPass456',
        }
        response = self.client.post(reverse('password_change'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('old_password', str(response.data).lower())

    def test_password_change_mismatch_400(self):
        """
        Несовпадение новых паролей должно возвращать 400.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')
        data = {
            'old_password': 'OldPass123',
            'new_password': 'NewPass456',
            'new_password2': 'DifferentPass789',
        }
        response = self.client.post(reverse('password_change'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('не совпадают', str(response.data))

    def test_password_change_short_new_400(self):
        """
        Слишком короткий новый пароль должен возвращать 400.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')
        data = {
            'old_password': 'OldPass123',
            'new_password': '123',
            'new_password2': '123',
        }
        response = self.client.post(reverse('password_change'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_change_without_auth_401(self):
        """
        Смена пароля без токена должна возвращать 401.
        """

        data = {
            'old_password': 'OldPass123',
            'new_password': 'NewPass456',
            'new_password2': 'NewPass456',
        }
        response = self.client.post(reverse('password_change'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_change_weak_password_400(self):
        """
        Слабый пароль (похожий на email) должен возвращать 400.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')
        data = {
            'old_password': 'OldPass123',
            'new_password': 'test@example.com123',
            'new_password2': 'test@example.com123',
        }
        response = self.client.post(reverse('password_change'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('new_password', str(response.data).lower())

    def _change_password(self):
        """
        Сменить пароль через API.

        :return: Ответ представления.
        """

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access}')
        data = {
            'old_password': 'OldPass123',
            'new_password': 'NewPass456',
            'new_password2': 'NewPass456',
        }
        return self.client.post(reverse('password_change'), data, format='json')

    def test_password_change_revokes_old_refresh(self):
        """
        После смены пароля старый refresh-токен должен отклоняться.
        """

        response = self._change_password()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.cookies['refresh_token'] = str(self.refresh)
        refresh_response = self.client.post(reverse('token-refresh'), format='json')

        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_change_revokes_all_user_tokens(self):
        """
        Смена пароля отзывает все выпущенные refresh-токены пользователя.
        """

        second_refresh = RefreshToken.for_user(self.user)

        response = self._change_password()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for token in (self.refresh, second_refresh):
            with self.subTest(token=str(token)[:20]):
                self.client.cookies['refresh_token'] = str(token)
                refresh_response = self.client.post(reverse('token-refresh'), format='json')
                self.assertEqual(
                    refresh_response.status_code,
                    status.HTTP_401_UNAUTHORIZED,
                )

    def test_login_after_password_change(self):
        """
        После смены пароля вход работает только с новым паролем.
        """

        response = self._change_password()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.credentials()

        login_new = self.client.post(
            reverse('login'),
            {'email': 'test@example.com', 'password': 'NewPass456'},
            format='json',
        )
        self.assertEqual(login_new.status_code, status.HTTP_200_OK)
        self.assertIn('access', login_new.data)

        login_old = self.client.post(
            reverse('login'),
            {'email': 'test@example.com', 'password': 'OldPass123'},
            format='json',
        )
        self.assertEqual(login_old.status_code, status.HTTP_400_BAD_REQUEST)
