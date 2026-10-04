from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
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
    description='Регистрация нового пользователя. Создает пользователя и возвращает данные пользователя (без password).',
    summary='Регистрация',
    tags=['auth'],
)

login_schema = extend_schema(
    request=serializers.LoginSerializer,
    responses={200: inline_serializer(
        name='LoginResponse',
        fields={
            'access': drf_serializers.CharField(
                help_text='Access-токен, хранить в памяти клиента',
            ),
            'user': UserSerializer(),
        },
    )},
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
    responses={200: OpenApiResponse(description='Пароль изменён')},
    description='Смена пароля пользователя.',
    summary='Смена пароля пользователя.',
    tags=['auth'],
)
