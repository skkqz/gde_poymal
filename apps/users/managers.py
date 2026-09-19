from django.contrib.auth.base_user import BaseUserManager



class UserManager(BaseUserManager):
    """
    Менеджер модели пользователя.
    """

    def create_user(self, email: str, password: str, **extra_fields) -> 'CustomUser':
        """
        Создание пользователя.
        :param email: Email пользователя.
        :param password: Пароль пользователя.
        :param extra_fields: Дополнительные поля.
        :return: Объект пользователя.
        """

        if not email:
            raise ValueError('Электронная почта обязательна для создания пользователя')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        return user


    def create_superuser(self, email: str, password: str, **extra_fields) -> 'CustomUser':
        """
        Создание суперпользователя.

        :param email: Email пользователя.
        :param password: Пароль пользователя.
        :param extra_fields: Дополнительные поля.
        :return: Объект пользователя.
        """

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff'):
            raise ValueError('Суперпользователь должен иметь is_staff=True')

        if extra_fields.get('is_superuser'):
            raise ValueError(
                'Суперпользователь должен иметь is_superuser=True',
            )

        return self.create_user(email, password, **extra_fields)
