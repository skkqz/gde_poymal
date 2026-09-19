from django.db import transaction


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
        :param args: позиционные аргументы маршрута.
        :param kwargs: именованные аргументы маршрута.
        :return: HTTP-ответ от родительского dispatch.
        """
        if request.method == "GET":
            return super(AtomicMixin, self).dispatch(request, *args, **kwargs)
        # Опасный запрос - POST, PUT ...
        with transaction.atomic():
            return super(AtomicMixin, self).dispatch(request, *args, **kwargs)

    def handle_exception(self, *args, **kwargs):
        """
        Обрабатывает исключение и откатывает транзакцию при ошибке.

        :param args: позиционные аргументы обработчика исключений.
        :param kwargs: именованные аргументы обработчика исключений.
        :return: HTTP-ответ с информацией об ошибке.
        """
        response = super(AtomicMixin, self).handle_exception(*args, **kwargs)

        if getattr(response, 'exception') and self.request.method != "GET":
            transaction.set_rollback(True)

        return response
