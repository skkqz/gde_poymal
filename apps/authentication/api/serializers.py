from typing import Any

from django.contrib.auth.handlers.modwsgi import check_password
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate

from rest_framework import serializers

from apps.users.api.schemas import user_schemas
from apps.users.models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор регистрации пользователя.
    """

    password = serializers.CharField(write_only=True, min_length=6, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, min_length=6, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = [
            'email',
            'password',
            'password2',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
        ]

    def validate_email(self, value: str) -> str:
        """
        Проверка и нормализация электронной почты.

        :param value: Электронная почта.
        :return: Нормализованная электронная почта.
        """

        value = value.strip().lower()

        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                'Пользователь с такой электронной почтой уже существует.'
            )

        return value

    def validate(self, attrs):
        """
        Проверка пароля.

        :param attrs: Даныне запроса.
        :return: Валидированные данные.
        """

        password1 = attrs.get('password')
        password2 = attrs.get('password2')

        if password1 != password2:
            raise serializers.ValidationError('Пароли не совпадают.')

        validate_password(password1, user=None)
        attrs.pop('password2')

        return attrs

    def create(self, validated_data: dict) -> CustomUser:
        """
        Создание пользователя.

        :param validated_data: Валидированные данные.
        :return:Созданный пользователь.
        """

        password = validated_data.pop('password')

        return CustomUser.objects.create_user(password=password, **validated_data)


class LoginSerializer(serializers.Serializer):
    """
    Сериализатор входа пользователя.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, attrs: dict) -> dict:
        """
        Проверка учётных данных пользователя.

        :param attrs: Данные запроса.
        :return: Валидированные данные с пользователем.
        """

        email = attrs['email'].strip().lower()
        password = attrs['password']

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )

        if user is None:
            raise serializers.ValidationError(
                'Не верная электронная почта или пароль.'
            )

        attrs['user'] = user

        return attrs


class LogoutSerializer(serializers.Serializer):
    """
    Сериализатор выхода пользователя.
    """

    refresh = serializers.CharField(write_only=True)


class TokenPairSerializer(serializers.Serializer):
    """Ответ с JWT парой."""

    access = serializers.CharField(help_text='Access токен')
    refresh = serializers.CharField(help_text='Refresh токен')


class PasswordChangeSerializer(serializers.Serializer):
    """
    Сериализатор смены пароля.
    """

    old_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate_old_password(self, value: str) -> str:
        """
        Проверяет текущий пароль пользователя.

        :param value: Текущий пароль.
        :return: Проверенный текущий пароль.
        """

        user = self.context['request'].user

        if not user.check_password(value):
            raise serializers.ValidationError('Неверно указан текущий пароль.')

        return value

    def validate_password(self, value: str) -> str:
        """
        Проверяет новый пароль согласно настройкам Django.

        :param value: Новый пароль.
        :return: Проверенный новый пароль.
        """

        user = self.context['request'].user

        validate_password(password=value, user=user)

        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """
        Проверяет совпадение новых паролей.

        :param attrs: Валидированные поля.
        :return: Валидированные данные.
        """

        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('Новые пароли не совпадают.')

        return attrs
