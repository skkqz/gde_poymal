import uuid

from django.db import models


class BaseModel(models.Model):
    """
    Абстрактная базовая модель.
    От неё должны наследоваться все модели.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата изменения',
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']
