from datetime import timedelta

from django.core.files.images import get_image_dimensions
from django.utils import timezone

from rest_framework import serializers

from apps.users.models import CustomUser


MAX_AVATAR_SIZE = 5 * 1024 * 1024
MAX_AVATAR_WIDTH = 4096
MAX_AVATAR_HEIGHT = 4096
MAX_USER_AGE = timedelta(days=150 * 365)


class AbsoluteImageField(serializers.ImageField):
    """
    ImageField с абсолютным URL и fallback при DisallowedHost.
    """

    def to_representation(self, value):
        if not value:
            return None
        try:
            url = value.url
        except Exception:
            return None
        request = self.context.get('request')
        if request is not None:
            try:
                return request.build_absolute_uri(url)
            except Exception:
                return url
        return url


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор пользователя.

    :param avatar: аватар, при отдаче — абсолютный URL, при загрузке — файл.
    """

    avatar = AbsoluteImageField(required=False, allow_null=True, allow_empty_file=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'birth_date', 'avatar', 'created_at', 'updated_at']
        extra_kwargs = {
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
        }

    def validate_first_name(self, value: str) -> str:
        """
        Нормализовать имя и запретить пустое значение.

        :param value: Имя из запроса.
        :return: Имя без ведущих и завершающих пробелов.
        :raises serializers.ValidationError: Если имя пустое.
        """

        value = value.strip()

        if not value:
            raise serializers.ValidationError('Имя не может быть пустым.')

        return value

    def validate_last_name(self, value: str) -> str:
        """
        Нормализовать фамилию и запретить пустое значение.

        :param value: Фамилия из запроса.
        :return: Фамилия без ведущих и завершающих пробелов.
        :raises serializers.ValidationError: Если фамилия пустая.
        """

        value = value.strip()

        if not value:
            raise serializers.ValidationError('Фамилия не может быть пустой.')

        return value

    def validate_birth_date(self, value):
        """
        Проверить реалистичность даты рождения.

        :param value: Дата рождения из запроса или None.
        :return: Проверенная дата рождения.
        :raises serializers.ValidationError: Если дата в будущем или возраст старше 150 лет.
        """

        if value is None:
            return value

        today = timezone.localdate()

        if value > today:
            raise serializers.ValidationError('Дата рождения не может быть в будущем.')

        if today - value > MAX_USER_AGE:
            raise serializers.ValidationError('Некорректная дата рождения.')

        return value

    def validate_avatar(self, value):
        """
        Проверить размер и габариты загружаемого аватара.

        Проверка формата уже выполнена ImageField: туда не проходят
        не-изображения и битые файлы. Здесь контролируем только вес
        и разрешение, чтобы не хранить гигантские файлы.

        :param value: Загруженный файл или None при очистке аватара.
        :return: Проверенный файл.
        :raises serializers.ValidationError: Если файл слишком большой.
        """

        if value is None:
            return value

        if value.size > MAX_AVATAR_SIZE:
            raise serializers.ValidationError(
                f'Размер аватара не должен превышать {MAX_AVATAR_SIZE // (1024 * 1024)} МБ.'
            )

        width, height = get_image_dimensions(value)

        if width is None or height is None:
            raise serializers.ValidationError('Не удалось определить размеры изображения.')

        if width > MAX_AVATAR_WIDTH or height > MAX_AVATAR_HEIGHT:
            raise serializers.ValidationError(
                f'Разрешение аватара не должно превышать {MAX_AVATAR_WIDTH}x{MAX_AVATAR_HEIGHT}.'
            )

        return value
