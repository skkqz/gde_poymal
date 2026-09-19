from drf_spectacular.utils import OpenApiResponse, extend_schema

from apps.authentication.api import serializers
from apps.users.api.serializers import UserSerializer


register_schema = extend_schema(
    request=serializers.RegisterSerializer,
    responses={201: UserSerializer},
    description='Регистрация нового пользователя. Создает пользователя и возвращает данные пользователя (без password).',
    summary='Регистрация',
    tags=['auth'],
)

login_schema = extend_schema(
    request=serializers.LoginSerializer,
    responses={200: serializers.TokenPairSerializer},
    description='Авторизация по email и паролю. Возвращает пару access/refresh токенов.',
    summary='Вход',
    tags=['auth'],
)

logout_schema = extend_schema(
    request=serializers.LogoutSerializer,
    responses={204: OpenApiResponse(description='Токен инвалидирован')},
    description='Выход. Инвалидирует refresh-токен (blacklist). Требует JWT.',
    summary='Выход',
    tags=['auth'],
)

me_schema = extend_schema(
    responses={200: UserSerializer},
    description='Возвращает данные текущего пользователя по JWT.',
    summary='Мой профиль',
    tags=['auth'],
)
