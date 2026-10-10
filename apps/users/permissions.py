from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.users.models import CustomUser


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Доступ владельца объекта или администратора.

    Чтение (безопасные методы) разрешено любому аутентифицированному
    пользователю, изменение и удаление — только владельцу объекта
    или администратору (is_staff / is_superuser).

    :cvar message: Сообщение ошибки при отказе в доступе.
    """

    message = 'Изменять можно только свои данные.'

    def has_permission(self, request: Request, view: APIView) -> bool:
        """
        Проверка доступа к представлению в целом.

        :param request: HTTP-запрос DRF.
        :param view: Представление, к которому обращаются.
        :return: True, если пользователь аутентифицирован.
        """

        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request: Request, view: APIView, obj: CustomUser) -> bool:
        """
        Проверка доступа к конкретному объекту.

        :param request: HTTP-запрос DRF.
        :param view: Представление, к которому обращаются.
        :param obj: Объект CustomUser, к которому запрашивается доступ.
        :return: True для безопасных методов; для остальных — если
            запрашивающий является владельцем объекта либо администратором.
        """

        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_staff or request.user.is_superuser:
            return True
        return obj.pk == request.user.pk
