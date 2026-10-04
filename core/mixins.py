from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import permissions


class AtomicMixin:
    """
    Миксин выполняющий каждый "Опасный" запрос внутри блока транзакций, в случаи ошибки делает rollback
        >>> from rest_framework.viewsets import ModelViewSet
        >>>
        >>>
        >>> class ViewSet(AtomicMixin, ModelViewSet):
        >>>     queryset = models.Model.objects.all()
        >>>     serializer_class = serializers.ModelSerializer
    """

    def dispatch(self, request, *args, **kwargs):
        """
        Диспетчеризует запрос с транзакционной защитой для небезопасных методов.

        :param request: HTTP-запрос.
        :param args: Позиционные аргументы маршрута.
        :param kwargs: Именованные аргументы маршрута.
        :return: HTTP-ответ от родительского dispatch.
        """
        if request.method in permissions.SAFE_METHODS: # GET, HEAD, OPTIONS
            return super().dispatch(request, *args, **kwargs)
        with transaction.atomic():
            return super().dispatch(request, *args, **kwargs)

    def handle_exception(self, exc, *args, **kwargs):
        """
        Обрабатывает исключение и откатывает транзакцию при ошибке.

        :param exc: Исключение.
        :param args: Позиционные аргументы обработчика исключений.
        :param kwargs: Именованные аргументы обработчика исключений.
        :return: HTTP-ответ с информацией об ошибке.
        """
        response = super().handle_exception(exc)
        if getattr(response, 'exception') and self.request.method != "GET":
            transaction.set_rollback(True)
        return response


class CsrfProtectMixin:
    """
    Включает CSRF-проверку для DRF-view.

    DRF по умолчанию освобождает все APIView от CsrfViewMiddleware
    (as_view() оборачивает view в csrf_exempt). Этот миксин
    возвращает защиту для эндпоинтов, которые аутентифицируются
    cookie без Authorization-заголовка: refresh, logout и любые
    другие state-changing операции.
    """

    @method_decorator(csrf_protect, name='dispatch')
    def dispatch(self, request, *args, **kwargs):
        """
        Проверить CSRF-токен перед обработкой запроса.

        :param request: HTTP запрос.
        :param args: Позиционные аргументы.
        :param kwargs: Именованные аргументы.
        :return: Ответ представления либо 403 при невалидном CSRF-токене.
        """
        return super().dispatch(request, *args, **kwargs)