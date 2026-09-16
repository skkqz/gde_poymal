from rest_framework import serializers

from apps.users.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор пользователя. Отдает только нужные поля, скрывает groups/user_permissions.

    """

    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=6,
        style={'input_type': 'password'},
        help_text='Пароль, минимум 6 символов.',
    )

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'password', 'first_name', 'last_name', 'birth_date', 'avatar', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def create(self, validated_data):
        """
        Создать пользователя через менеджер с хешированием пароля.

        :param validated_data: валидированные данные с password.
        :return: созданный CustomUser.
        """
        password = validated_data.pop('password')
        return CustomUser.objects.create_user(password=password, **validated_data)

    def update(self, instance, validated_data):
        """
        Обновить пользователя, хеширует пароль если передан.

        :param instance: экземпляр CustomUser.
        :param validated_data: данные для обновления.
        :return: обновленный CustomUser.
        """
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
