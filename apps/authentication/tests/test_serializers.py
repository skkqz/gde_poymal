from django.test import TestCase

from apps.users.models import CustomUser
from apps.authentication.api.serializers import (
    RegisterSerializer,
    LoginSerializer,
    LogoutSerializer,
    TokenPairSerializer,
)


class RegisterSerializerTest(TestCase):
    """Тесты RegisterSerializer."""

    def test_valid_registration(self):
        """
        Валидная регистрация пользователя.
        """

        data = {
            'email': 'new@example.com',
            'password': 'StrongPass123',
            'password2': 'StrongPass123',
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.email, 'new@example.com')
        self.assertTrue(user.check_password('StrongPass123'))

    def test_password_mismatch_raises(self):
        """
        Несовпадение паролей должно вызывать ошибку.
        """

        data = {
            'email': 'test@example.com',
            'password': 'StrongPass123',
            'password2': 'DifferentPass123',
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('Пароли не совпадают', str(serializer.errors))

    def test_duplicate_email_raises(self):
        """
        Дубликат email должен вызывать ошибку.
        """

        CustomUser.objects.create_user(
            email='existing@example.com',
            password='StrongPass123',
        )
        data = {
            'email': 'existing@example.com',
            'password': 'StrongPass123',
            'password2': 'StrongPass123',
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('Пользователь с таким Электронная почта уже существует.', str(serializer.errors))

    def test_email_normalization(self):
        """
        Email должен нормализоваться к нижнему регистру.
        """

        data = {
            'email': 'User@EXAMPLE.COM',
            'password': 'StrongPass123',
            'password2': 'StrongPass123',
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.email, 'user@example.com')

    def test_short_password_raises(self):
        """
        Короткий пароль должен вызывать ошибку валидации.
        """

        data = {
            'email': 'test@example.com',
            'password': '123',
            'password2': '123',
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class LoginSerializerTest(TestCase):
    """Тесты LoginSerializer."""

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='StrongPass123',
        )

    def test_valid_login(self):
        """
        Валидный вход пользователя.
        """

        data = {
            'email': 'test@example.com',
            'password': 'StrongPass123',
        }
        serializer = LoginSerializer(data=data, context={'request': None})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['user'], self.user)

    def test_invalid_password_raises(self):
        """
        Неверный пароль должен вызывать ошибку.
        """

        data = {
            'email': 'test@example.com',
            'password': 'WrongPass123',
        }
        serializer = LoginSerializer(data=data, context={'request': None})
        self.assertFalse(serializer.is_valid())
        self.assertIn('Не верная', str(serializer.errors))

    def test_nonexistent_user_raises(self):
        """
        Несуществующий пользователь должен вызывать ошибку.
        """

        data = {
            'email': 'nonexistent@example.com',
            'password': 'StrongPass123',
        }
        serializer = LoginSerializer(data=data, context={'request': None})
        self.assertFalse(serializer.is_valid())
        self.assertIn('Не верная', str(serializer.errors))

    def test_email_case_insensitive(self):
        """
        Вход должен быть нечувствителен к регистру email.
        """

        data = {
            'email': 'TEST@EXAMPLE.COM',
            'password': 'StrongPass123',
        }
        serializer = LoginSerializer(data=data, context={'request': None})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data['user'], self.user)


class LogoutSerializerTest(TestCase):
    """Тесты LogoutSerializer."""

    def test_valid_refresh(self):
        """
        Валидный refresh токен.
        """

        data = {'refresh': 'some_refresh_token'}
        serializer = LogoutSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['refresh'], 'some_refresh_token')

    def test_missing_refresh_raises(self):
        """
        Отсутствие refresh токена должно вызывать ошибку.
        """

        serializer = LogoutSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertIn('refresh', serializer.errors)


class TokenPairSerializerTest(TestCase):
    """Тесты TokenPairSerializer."""

    def test_serialization(self):
        """
        Сериализация пары токенов.
        """

        data = {
            'access': 'access_token_string',
            'refresh': 'refresh_token_string',
        }
        serializer = TokenPairSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data, data)
