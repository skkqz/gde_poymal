from django.db import models

from core.models import BaseModel


class EmailVerificationToken(BaseModel):
    """
    Токен подтверждения email пользовательской почты.

    Создаётся при регистрации и при повторной отправке письма.
    Используется один раз, имеет ограниченный срок жизни.
    """

    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='email_verification_tokens',
        verbose_name='Пользователь',
    )
    token = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        verbose_name='Токен',
    )
    expires_at = models.DateTimeField(
        verbose_name='Дата истечения',
    )
    used = models.BooleanField(
        default=False,
        verbose_name='Использован',
    )

    class Meta:
        db_table = '"s_accounts"."t_email_verification_tokens"'
        verbose_name = 'Токен подтверждения email'
        verbose_name_plural = 'Токены подтверждения email'
        ordering = ('-created_at',)

    def __str__(self) -> str:
        """
        Строковое представление токена.

        :return: Токен и email пользователя.
        """

        return f'{self.token[:16]}... ({self.user.email})'
