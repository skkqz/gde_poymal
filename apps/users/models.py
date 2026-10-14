from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from apps.users.managers import UserManager
from apps.users.services.path_avatar import user_avatar_upload_to
from core.models import BaseModel


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
        upload_to=user_avatar_upload_to,
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

    password = models.CharField(
        max_length=128,
        verbose_name='Пароль',
    )
    last_login = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Последний вход',
    )
    is_superuser = models.BooleanField(
        default=False,
        verbose_name='Суперпользователь',
        help_text='Обозначает, что пользователь имеет все права без их явного назначения.',
    )
    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        verbose_name='Группы',
        help_text=(
            'Группы, к которым принадлежит пользователь. '
            'Пользователь получит все права, предоставленные каждой из его групп.'
        ),
        related_name='user_set',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        verbose_name='Права пользователя',
        help_text='Конкретные права этого пользователя.',
        related_name='user_set',
        related_query_name='user',
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

        old_avatar_name = None

        if self.pk:
            try:
                old = CustomUser.objects.get(pk=self.pk)
                if old.avatar and old.avatar.name != (self.avatar.name if self.avatar else None):
                    old_avatar_name = old.avatar.name
            except CustomUser.DoesNotExist:
                old_avatar_name = None

        super().save(*args, **kwargs)

        if old_avatar_name:
            try:
                self.avatar.storage.delete(old_avatar_name)
            except Exception:
                pass

    def delete(self, *args, **kwargs):
        """
        Удалить пользователя вместе с файлом аватара.

        :param args: Позиционные аргументы.
        :param kwargs: Именованные аргументы.
        """

        avatar_name = self.avatar.name if self.avatar else None
        super().delete(*args, **kwargs)
        if avatar_name:
            try:
                self.avatar.storage.delete(avatar_name)
            except Exception:
                pass

    def __str__(self) -> str:
        """
        Строковое представление пользователя

        :return: Email пользователя
        """

        return str(self.email)
