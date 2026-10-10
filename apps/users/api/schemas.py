from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view

from apps.users.api.serializers import UserSerializer

user_schemas = extend_schema_view(
    retrieve=extend_schema(
        summary='Профиль пользователя',
        description='Возвращает профиль пользователя по UUID. Требует JWT.',
        tags=['users'],
        responses={200: UserSerializer},
    ),
    list=extend_schema(
        summary='Список пользователей',
        description='Возвращает список пользователей с пагинацией '
                    '(PageNumberPagination, 20 на страницу). Временный эндпоинт, '
                    'будет заменён поиском.',
        tags=['users'],
    ),
    partial_update=extend_schema(
        summary='Обновить пользователя',
        description='Частичное обновление профиля. PUT отключён. '
                    'Обновляемые поля: first_name, last_name, birth_date, avatar. '
                    'Email — только для чтения. '
                    'Скалярные поля — JSON, аватар — multipart/form-data. '
                    'Изменять можно только свой профиль (или админу).',
        tags=['users'],
        request=UserSerializer,
        responses={
            200: UserSerializer,
            400: OpenApiResponse(description='Ошибка валидации'),
            403: OpenApiResponse(description='Нет прав на изменение чужого профиля'),
        },
    ),
    destroy=extend_schema(
        summary='Удалить пользователя',
        description='Удаляет пользователя по UUID вместе с файлом аватара. '
                    'Удалять можно только себя (или админу).',
        tags=['users'],
        responses={
            204: OpenApiResponse(description='Пользователь удалён'),
            403: OpenApiResponse(description='Нет прав на удаление чужого профиля'),
        },
    ),
)
