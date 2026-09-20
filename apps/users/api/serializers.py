from rest_framework import serializers

from apps.users.models import CustomUser


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
