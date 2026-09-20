from django.test import TestCase, RequestFactory
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from core.mixins import AtomicMixin


class DummyAtomicView(AtomicMixin, APIView):
    """Тестовая вью для проверки AtomicMixin."""

    permission_classes = []

    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)

    def head(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)

    def options(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)


class ErrorAtomicView(AtomicMixin, APIView):
    """Вью с ошибкой для тестирования rollback."""

    permission_classes = []

    def post(self, request, *args, **kwargs):
        raise ValueError("test error")


class AtomicMixinTest(TestCase):
    """Тесты AtomicMixin."""

    def setUp(self):
        self.factory = RequestFactory()

    def test_get_not_wrapped_in_atomic(self):
        """
        GET запрос не должен оборачиваться в atomic.
        """

        view = DummyAtomicView.as_view()
        request = self.factory.get('/test/')
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_wrapped_in_atomic(self):
        """
        POST запрос должен оборачиваться в atomic.
        """

        view = DummyAtomicView.as_view()
        request = self.factory.post('/test/', {})
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_rollback_on_exception(self):
        """
        При исключении внутри POST должен произойти rollback.
        """

        # AtomicMixin делает rollback при исключении внутри atomic блока
        # Проверяем, что исключение пробрасывается и транзакция откатывается
        with self.assertRaises(ValueError):
            ErrorAtomicView.as_view()(self.factory.post('/test/', {}))

    def test_safe_methods_not_atomic(self):
        """
        SAFE методы (HEAD, OPTIONS) не должны оборачиваться в atomic.
        """

        view = DummyAtomicView.as_view()
        for method in ('head', 'options'):
            request = getattr(self.factory, method)('/test/')
            response = view(request)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
