from loguru import logger

from apps.authentication.services.jwt_service import JWTService
from apps.users.models import CustomUser


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
        user.save(update_fields=['password', 'updated_at'])

        JWTService.revoke_all_refresh_tokens(user)

        logger.debug(
            f'Пароль пользователя обновлён в БД (user_id={user.pk})',
        )
