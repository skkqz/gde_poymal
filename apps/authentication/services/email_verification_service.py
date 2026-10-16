import secrets
from datetime import timedelta

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from loguru import logger

from apps.authentication.models import EmailVerificationToken
from apps.users.models import CustomUser


TOKEN_EXPIRY_HOURS = 24  # Время жизни токена в часах
TOKEN_LENGTH = 64  # Длина токена в символах


class EmailVerificationService:
    """
    Сервис подтверждения email: генерация токенов, отправка писем, проверка.
    """

    @staticmethod
    def create_token(user: CustomUser) -> EmailVerificationToken:
        """
        Создать токен подтверждения.

        Инвалидирует все предыдущие неиспользованные токены пользователя.

        :param user: Пользователь.
        :return: Созданный токен.
        """

        EmailVerificationToken.objects.filter(user=user, used=False).update(used=True)

        token = EmailVerificationToken.objects.create(
            user=user,
            token=secrets.token_urlsafe(TOKEN_LENGTH)[:TOKEN_LENGTH],
            expires_at=timezone.now() + timedelta(hours=TOKEN_EXPIRY_HOURS),
        )

        logger.debug(
            f'Создан токен подтверждения email (user_id={user.pk})',
        )

        return token

    @staticmethod
    def send_verification_email(user: CustomUser, token: EmailVerificationToken) -> None:
        """
        Отправить письмо с подтверждением email.

        :param user: Пользователь.
        :param token: Токен подтверждения.
        """
        subject = "Подтвердите email — Где поймал?"

        # Ссылка: пока localhost для локальной отладки. На сервере (Astra Linux) замени на реальный домен
        verify_url = f"http://localhost:3000/verify-email?token={token.token}"

        context = {
            "user": user,
            "token": token.token,
            "expiry_hours": TOKEN_EXPIRY_HOURS,
            "verify_url": verify_url,
        }

        html_message = render_to_string("authentication/email_verification.html", context)
        plain_message = strip_tags(html_message)

        try:
            send_mail(
                subject=subject,
                message=plain_message,  # plain-text версия (обязательно)
                from_email=None,  # берётся из MAILERS['default']['FROM_EMAIL']
                recipient_list=[user.email],
                html_message=html_message,  # HTML-версия (именно сюда!)
                fail_silently=False,  # для отладки: чтобы видеть ошибки SMTP
            )
            logger.debug(
                f"Письмо подтверждения отправлено (user_id={user.pk}, email={user.email})"
            )
        except Exception as e:
            logger.exception(
                f"Не удалось отправить письмо подтверждения (user_id={user.pk}, email={user.email}): {e}"
            )
            raise

    @staticmethod
    def verify_token(token_str: str) -> CustomUser:
        """
        Проверить токен и подтвердить email.

        :param token_str: Токен из письма.
        :return: Пользователь с подтверждённым email.
        :raises ValueError: Токен невалиден, истёк или уже использован.
        """

        try:
            token = EmailVerificationToken.objects.get(token=token_str)
        except EmailVerificationToken.DoesNotExist:
            logger.warning(f'Токен подтверждения не найден: {token_str[:16]}...')
            raise ValueError('Токен не найден')

        if token.used:
            logger.warning(
                f'Токен подтверждения уже использован (user_id={token.user.pk})',
            )
            raise ValueError('Токен уже использован')

        if timezone.now() > token.expires_at:
            logger.warning(
                f'Токен подтверждения истёк (user_id={token.user.pk})',
            )
            raise ValueError('Токен истёк')

        token.used = True
        token.save(update_fields=['used'])

        user = token.user
        user.is_email_verified = True
        user.save(update_fields=['is_email_verified', 'updated_at'])

        logger.info(
            f'Email подтверждён (user_id={user.pk} email={user.email})',
        )

        return user

    @staticmethod
    def resend_verification(user: CustomUser) -> EmailVerificationToken | None:
        """
        Создать и отправить новый токен.

        Если email уже подтверждён — возвращает None.

        :param user: Пользователь.
        :return: Новый токен или None.
        """

        if user.is_email_verified:
            logger.debug(
                f'Повторная отправка не нужна, email уже подтверждён (user_id={user.pk})',
            )
            return None

        token = EmailVerificationService.create_token(user)
        EmailVerificationService.send_verification_email(user, token)

        logger.info(
            f'Повторное письмо отправлено (user_id={user.pk} email={user.email})',
        )

        return token
