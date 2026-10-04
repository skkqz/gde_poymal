from rest_framework.viewsets import ModelViewSet

from apps.users.api.schemas import user_schemas
from apps.users.models import CustomUser
from apps.users.api.serializers import UserSerializer
from core.mixins import AtomicMixin


@user_schemas
class UserView(AtomicMixin, ModelViewSet):
    """
    Представление пользователя.
    """

    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer



