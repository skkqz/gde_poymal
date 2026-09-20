from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.users.api.serializers import UserSerializer

user_schemas = extend_schema_view(
    retrieve=extend_schema(
        summary='Профиль пользователя',
        description='Возвращает профиль по UUID. Требует JWT.',
        tags=['users'],
    ),
    list=extend_schema(
        summary='Список пользователей',
        description='Возвращает список пользователей (для админки/поиска).',
        tags=['users'],
    ),
    partial_update=extend_schema(
        summary='Обновить пользователя',
        description='Частичное обновление PATCH. PUT отключен. Требует JWT.',
        tags=['users'],
        request=UserSerializer,
        responses={200: UserSerializer},
    ),
    destroy=extend_schema(
        summary='Удалить пользователя',
        description='Удаляет пользователя по UUID. Требует JWT.',
        tags=['users'],
    ),
)
