from core.models import BaseModel
from apps.users.managers import UserManager

from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin


class CustomUser(BaseModel, AbstractBaseUser, PermissionsMixin):
    """
    Кастомная модель пользователя
    """

    email = models.EmailField(
        unique=True,
        db_index=True,
        verbose_name='Email',
    )
    first_name = models.CharField(
        max_length=255,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=255,
        verbose_name='Фамилия',
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата рождения',
    )
    avatar = models.ImageField(
        upload_to='users/avatars/',
        null=True,
        blank=True,
        verbose_name='Аватар',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен',
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name='Персонал',
    )
    is_email_verified = models.BooleanField(
        default=False,
        verbose_name='Email подтвержден',
    )

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = '"s_accounts"."t_users"'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        """
        Строковое представление пользователя

        :return: Email пользователя
        """

        return str(self.email)

