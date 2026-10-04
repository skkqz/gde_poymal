from django.urls import path

from apps.users.api import views

urlpatterns = [
    path('<uuid:pk>/', views.UserView.as_view({
        'get': 'retrieve',
        'patch': 'partial_update',
        'delete': 'destroy',
    }), name='user_detail'),
    path('all/', views.UserView.as_view({'get': 'list'}), name='user_all') # todo Убрать когда появиться поиск пользователей
]
