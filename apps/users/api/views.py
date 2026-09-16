from rest_framework.viewsets import ModelViewSet

from core.mixins import AtomicMixin
from apps.users.models import CustomUser
from apps.users.api.serializers import UserSerializer


class UserView(AtomicMixin, ModelViewSet):
    """
    Представление пользователя. Отдает только нужные поля.
    """

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer



