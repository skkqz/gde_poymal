import secrets
from datetime import timedelta

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from loguru import logger

from apps.authentication.models import PasswordResetToken
from apps.authentication.services.jwt_service import JWTService
from apps.users.models import CustomUser

RESET_TOKEN_EXPIRY_HOURS = 1
RESET_TOKEN_LENGTH = 64
RATE_LIMIT_MINUTES = 10


class PasswordResetService:
    """
    Сервис восстановления пароля.

    Генерирует токены, отправляет письма, проверяет токены,
    сбрасывает пароль.
    """

    @staticmethod
    def can_request_reset(user: CustomUser) -> bool:
        """
        Проверить, можно ли запросить новый токен (rate-limit).

        Не чаще 1 раза в RATE_LIMIT_MINUTES минут.

        :param user: Пользователь.
        :return: True, если можно создать новый токен.
        """

        recent = PasswordResetToken.objects.filter(
            user=user,
            created_at__gte=timezone.now() - timedelta(minutes=RATE_LIMIT_MINUTES),
            used=False,
        ).exists()

        return not recent

    @staticmethod
    def create_reset_token(user: CustomUser) -> PasswordResetToken:
        """
        Создать токен восстановления пароля.

        Инвалидирует все предыдущие неиспользованные токены пользователя.

        :param user: Пользователь.
        :return: Созданный токен.
        """

        PasswordResetToken.objects.filter(user=user, used=False).update(used=True)

        token = PasswordResetToken.objects.create(
            user=user,
            token=secrets.token_urlsafe(RESET_TOKEN_LENGTH)[:RESET_TOKEN_LENGTH],
            expires_at=timezone.now() + timedelta(hours=RESET_TOKEN_EXPIRY_HOURS),
        )

        logger.debug(f'Создан токен восстановления пароля (user_id={user.pk})')

        return token

    @staticmethod
    def send_reset_email(user: CustomUser, token: PasswordResetToken) -> None:
        """
        Отправить письмо с ссылкой для восстановления пароля.

        :param user: Пользователь.
        :param token: Токен восстановления.
        """

        subject = 'Восстановление пароля — Где поймал?'

        html_content = render_to_string(
            'authentication/password_reset.html',
            {'user': user, 'token': token.token, 'expiry_hours': RESET_TOKEN_EXPIRY_HOURS},
        )

        email = EmailMultiAlternatives(
            subject=subject,
            body=html_content,
            from_email=None,
            to=[user.email],
        )
        email.content_subtype = 'html'
        email.send(fail_silently=True)

        logger.debug(f'Письмо восстановления пароля отправлено (user_id={user.pk} email={user.email})')

    @staticmethod
    def reset_password(token_str: str, new_password: str) -> CustomUser:
        """
        Проверить токен и установить новый пароль.

        После успеха все refresh-токены пользователя отзываются.

        :param token_str: Токен из письма.
        :param new_password: Новый пароль.
        :return: Пользователь с обновлённым паролем.
        :raises ValueError: Токен невалиден, истёк или уже использован.
        """

        try:
            token = PasswordResetToken.objects.get(token=token_str)
        except PasswordResetToken.DoesNotExist:
            logger.warning(f'Токен восстановления не найден: {token_str[:16]}...')
            raise ValueError('Токен не найден') from None

        if token.used:
            logger.warning(
                f'Токен восстановления уже использован (user_id={token.user.pk})',
            )
            raise ValueError('Токен уже использован')

        if timezone.now() > token.expires_at:
            logger.warning(
                f'Токен восстановления истёк (user_id={token.user.pk})',
            )
            raise ValueError('Токен истёк')

        token.used = True
        token.save(update_fields=['used'])

        user = token.user
        user.set_password(new_password)
        user.save(update_fields=['password', 'updated_at'])

        JWTService.revoke_all_refresh_tokens(user)

        logger.info(f'Пароль восстановлен (user_id={user.pk} email={user.email})')

        return user
