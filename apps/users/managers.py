from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """
    Менеджер модели пользователя.
    """

    def create_user(self, email: str, password: str, **extra_fields) -> 'User':
        """
        Создание пользователя.
        :param email: Email пользователя.
        :param password: Пароль пользователя.
        :param extra_fields: Дополнительные поля.
        :return: Объект пользователя.
        """

        if not email:
            raise ValueError('Email обязателен для создания пользователя')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        return user


    def create_superuser(self, email: str, password: str, **extra_fields) -> 'User':
        """
        Создание суперпользователя.

        :param email: Email пользователя.
        :param password: Пароль пользователя.
        :param extra_fields: Дополнительные поля.
        :return: Объект пользователя.
        """

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)


        return self.create_user(email, password, **extra_fields)
