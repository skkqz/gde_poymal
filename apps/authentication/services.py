from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import CustomUser


class JWTService:
    """
    Класс сервис для работы с JWT токенами.
    """

    @staticmethod
    def create_token_pair(user: CustomUser) -> dict[str, str]:
        """
        Создание пары access/refresh токенов.

        :param user: Пользователь.
        :return: Access и refresh токены.
        """

        refresh = RefreshToken.for_user(user)

        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }

    @staticmethod
    def blacklist_refresh_token(user: CustomUser,  refresh_token: str) -> None:
        """
        Добавление refresh токена в blacklist.

        :param user: Пользователь.
        :param refresh_token: Refresh токен.
        """
        try:
            token = RefreshToken(refresh_token)
        except TokenError as exc:
            raise ValidationError('Некорректный refresh токен.') from exc

        user_id_claim = api_settings.USER_ID_CLAIM

        if str(token.get(user_id_claim)) != str(user.pk):
            raise ValidationError('Refresh токен принадлежит другому пользователю.')

        token.blacklist()


class PasswordService:
    """
    Сервис работы с паролем пользователя.
    """

    @staticmethod
    def change_password(user: CustomUser, new_password: str) -> None:
        """
        Изменение пароля пользователя.

        :param user: Пользователь.
        :param new_password: Новый пароль пользователя.
        """

        user.set_password(new_password)
        user.save(update_fields=['password', 'updated_at', ])
