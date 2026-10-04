import os

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
        verbose_name='Электронная почта',
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

    def save(self, *args, **kwargs):
        """
        Сохранить пользователя, удалив старый аватар если он изменен.

        :param args: Позиционные аргументы.
        :param kwargs: Именованные аргументы.
        """

        if self.pk:
            try:
                old = CustomUser.objects.get(pk=self.pk)
                if old.avatar and old.avatar != self.avatar:
                    if old.avatar.name and os.path.isfile(old.avatar.path):
                        try:
                            os.remove(old.avatar.path)
                        except (ValueError, OSError):
                            pass
                # если аватар очистили, удалить старый
                if not self.avatar and old.avatar:
                    if old.avatar.name and os.path.isfile(old.avatar.path):
                        try:
                            os.remove(old.avatar.path)
                        except (ValueError, OSError):
                            pass
            except CustomUser.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Удалить пользователя вместе с файлом аватара.

        :param args: Позиционные аргументы.
        :param kwargs: Именованные аргументы.
        """

        if self.avatar and self.avatar.name:
            try:
                if os.path.isfile(self.avatar.path):
                    os.remove(self.avatar.path)
            except (ValueError, OSError):
                pass
        super().delete(*args, **kwargs)

    def __str__(self) -> str:
        """
        Строковое представление пользователя

        :return: Email пользователя
        """

        return str(self.email)
