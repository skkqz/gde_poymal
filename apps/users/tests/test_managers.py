from django.test import TestCase

from apps.users.models import CustomUser


class UserManagerTest(TestCase):
    """Тесты менеджера пользователей."""

    def test_create_user_ok(self):
        """
        Создание обычного пользователя.
        """

        user = CustomUser.objects.create_user(
            email='test@example.com',
            password='StrongPass123',
            first_name='Ivan',
            last_name='Ivanov',
        )

        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('StrongPass123'))
        self.assertEqual(user.first_name, 'Ivan')
        self.assertEqual(user.last_name, 'Ivanov')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_create_user_no_email_raises(self):
        """
        Без email должно подниматься ValueError.
        """

        with self.assertRaises(ValueError) as cm:
            CustomUser.objects.create_user(email='', password='StrongPass123')
        self.assertIn('Электронная почта обязательна для создания пользователя', str(cm.exception))

    def test_create_user_email_normalized(self):
        """
        Email должен нормализоваться (приводиться к нижнему регистру).
        """

        user = CustomUser.objects.create_user(
            email='User@EXAMPLE.COM',
            password='StrongPass123',
        )
        self.assertEqual(user.email, 'user@example.com')

    def test_create_user_duplicate_email_raises(self):
        """
        Дубликат email должен вызывать IntegrityError.
        """

        CustomUser.objects.create_user(
            email='duplicate@example.com',
            password='StrongPass123',
        )
        with self.assertRaises(Exception):  # IntegrityError
            CustomUser.objects.create_user(
                email='duplicate@example.com',
                password='AnotherPass123',
            )

    def test_create_superuser_ok(self):
        """
        Создание суперпользователя.
        """

        user = CustomUser.objects.create_superuser(
            email='admin@example.com',
            password='AdminPass123',
        )

        self.assertEqual(user.email, 'admin@example.com')
        self.assertTrue(user.check_password('AdminPass123'))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_create_superuser_without_staff_raises(self):
        """
        create_superuser без is_staff должен вызывать ValueError.
        """

        with self.assertRaises(ValueError) as cm:
            CustomUser.objects.create_superuser(
                email='admin2@example.com',
                password='AdminPass123',
                is_staff=False,
            )
        self.assertIn('is_staff', str(cm.exception))

    def test_create_superuser_without_superuser_raises(self):
        """
        create_superuser без is_superuser должен вызывать ValueError.
        """

        with self.assertRaises(ValueError) as cm:
            CustomUser.objects.create_superuser(
                email='admin3@example.com',
                password='AdminPass123',
                is_superuser=False,
            )
        self.assertIn('is_superuser', str(cm.exception))
