from django.urls import path, re_path, include
from .views import RegisterUser, UserLogin, GetAllUsers, UserGetUpdateDelete, ListUserAllLogs, ListCreateLog, SelectedLog

urlpatterns = [
    path('api/register/', RegisterUser.as_view(), name='register-user'),
    path('api/login/', UserLogin.as_view(), name='user-login'),

    path('api/logs/', ListCreateLog.as_view(), name='list-post-errors'),
    path('api/logs/<str:pk>/', SelectedLog.as_view(), name='get-error'),

    path('api/users/', GetAllUsers.as_view(), name='list-all-users'),
    path('api/users/<int:pk>/', UserGetUpdateDelete.as_view(), name='get-user'),
    path('api/users/<int:pk>/logs/', ListUserAllLogs.as_view(), name='list-user-all-errors')
]

