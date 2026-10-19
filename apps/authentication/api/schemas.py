from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers as drf_serializers

from apps.authentication.api import serializers
from apps.users.api.serializers import UserSerializer

csrf_schema = extend_schema(
    request=None,
    responses={204: OpenApiResponse(description='CSRF-cookie установлена')},
    description='Bootstrap-эндпоинт для SPA. Устанавливает читаемую из JS '
    'csrftoken-cookie. Вызывается один раз при загрузке приложения, '
    'до любых cookie-authenticated POST-запросов.',
    summary='Выдача CSRF-cookie',
    tags=['auth'],
)

register_schema = extend_schema(
    request=serializers.RegisterSerializer,
    responses={201: UserSerializer},
    description='Регистрация нового пользователя.'
    ' Создает пользователя и возвращает данные пользователя (без password).',
    summary='Регистрация',
    tags=['auth'],
)

login_schema = extend_schema(
    request=serializers.LoginSerializer,
    responses={
        200: inline_serializer(
            name='LoginResponse',
            fields={
                'access': drf_serializers.CharField(
                    help_text='Access-токен, хранить в памяти клиента',
                ),
                'user': UserSerializer(),
            },
        )
    },
    description='Авторизация по email и паролю. Access-токен и данные пользователя '
    'возвращаются в теле ответа, refresh-токен устанавливается '
    'в HttpOnly cookie.',
    summary='Вход',
    tags=['auth'],
)

refresh_schema = extend_schema(
    request=None,
    responses={200: serializers.AccessTokenResponse},
    description='Обновление access-токена. Refresh-токен читается из HttpOnly cookie, '
    'тело запроса не требуется. При включённой ротации новый refresh-токен '
    'возвращается в обновлённой cookie. Требует заголовок X-CSRFToken.',
    summary='Обновление access-токена',
    tags=['auth'],
)

logout_schema = extend_schema(
    request=None,
    responses={204: OpenApiResponse(description='Сессия завершена, refresh-cookie удалена')},
    description='Выход. Инвалидирует refresh-токен из HttpOnly cookie (blacklist) '
    'и удаляет cookie с клиента. Требует JWT в заголовке Authorization '
    'и заголовок X-CSRFToken. Тело запроса не требуется.',
    summary='Выход',
    tags=['auth'],
)

password_change = extend_schema(
    request=serializers.PasswordChangeSerializer,
    responses={
        200: OpenApiResponse(description='Пароль изменён, все ранее выданные refresh-токены отозваны'),
        400: OpenApiResponse(description='Ошибка валидации'),
    },
    description='Смена пароля пользователя. После успешной смены все ранее '
    'выпущенные refresh-токены пользователя попадают в blacklist '
    'и перестают работать. Требует JWT.',
    summary='Смена пароля пользователя.',
    tags=['auth'],
)

verify_email_schema = extend_schema(
    request=None,
    parameters=[
        OpenApiParameter(
            name='token',
            type=str,
            location=OpenApiParameter.QUERY,
            required=True,
            description='Токен подтверждения из письма',
        ),
    ],
    responses={
        200: UserSerializer,
        400: OpenApiResponse(
            description='Токен не предоставлен, невалиден, истёк или уже использован',
        ),
    },
    description='Подтверждение email по токену из письма.',
    summary='Подтверждение email',
    tags=['auth'],
)

resend_verification_schema = extend_schema(
    request=None,
    responses={
        200: OpenApiResponse(description='Письмо отправлено'),
        400: OpenApiResponse(description='Email уже подтверждён'),
    },
    description='Повторная отправка письма подтверждения email. Требует JWT. '
    'Инвалидирует предыдущий токен и отправляет новый.',
    summary='Повторная отправка письма подтверждения',
    tags=['auth'],
)

request_password_reset_schema = extend_schema(
    request=serializers.RequestPasswordResetSerializer,
    responses={
        200: OpenApiResponse(description='Письмо отправлено'),
    },
    description='Запрос восстановления пароля. Ототправляет письмо с токеном '
                'на email пользователя. Не раскрывает, существует ли email. '
                'Rate-limit: 1 раз в 10 минут.',
    summary='Запрос восстановления пароля',
    tags=['auth'],
)

confirm_password_reset_schema = extend_schema(
    request=serializers.ConfirmPasswordResetSerializer,
    responses={
        200: OpenApiResponse(description='Пароль изменён'),
        400: OpenApiResponse(description='Ошибка валидации или невалидный токен'),
    },
    description='Установка нового пароля по токену из письма. После успеха '
                'все ранее выданные refresh-токены отзываются.',
    summary='Подтверждение восстановления пароля',
    tags=['auth'],
)
