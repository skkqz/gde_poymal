from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)

from loguru import logger

from apps.users.models import CustomUser


class JWTService:
    """
    Класс сервис для работы с JWT токенами.
    """

    @staticmethod
    def blacklist_refresh_token(user: CustomUser, refresh_token: str) -> None:
        """
        Добавление refresh токена в blacklist.

        :param user: Пользователь.
        :param refresh_token: Refresh токен.
        :raises ValidationError: Если токен невалиден или принадлежит другому пользователю.
        """

        try:
            token = RefreshToken(refresh_token)
        except TokenError as exc:
            logger.warning(
                f'Блэклист отклонён: невалидный refresh-токен '
                f'(user_id={user.pk}, ошибка={exc})',
            )
            raise ValidationError('Некорректный refresh токен.') from exc

        user_id_claim = api_settings.USER_ID_CLAIM
        token_user_id = token.get(user_id_claim)

        if str(token_user_id) != str(user.pk):
            logger.warning(
                f'Блэклист отклонён: refresh-токен принадлежит другому пользователю '
                f'(user_id={user.pk}, token_user_id={token_user_id})',
            )
            raise ValidationError('Refresh токен принадлежит другому пользователю.')

        token.blacklist()

        logger.debug(
            f'Refresh-токен добавлен в блэклист (user_id={user.pk})',
        )

    @staticmethod
    def revoke_all_refresh_tokens(user: CustomUser) -> int:
        """
        Добавить в blacklist все выпущенные refresh-токены пользователя.

        Вызывается при смене пароля: старые сессии должны умереть вместе
        со старым паролем, иначе смена пароля не защищает от компрометации.

        :param user: Пользователь.
        :return: Количество вновь забаненных токенов.
        """

        revoked = 0
        outstanding = OutstandingToken.objects.filter(user=user)

        for token in outstanding:
            _, created = BlacklistedToken.objects.get_or_create(token=token)
            if created:
                revoked += 1

        logger.debug(
            f'Отозваны refresh-токены пользователя (user_id={user.pk}, count={revoked})',
        )

        return revoked