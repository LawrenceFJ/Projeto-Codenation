from django.urls import path, re_path, include
from .views import RegisterUser, UserLogin, GetAllUsers, UserGetUpdateDelete, ListUserAllLogs, ListCreateLog, SelectedLog

urlpatterns = [
    path('register/', RegisterUser.as_view(), name='register-user'),
    path('login/', UserLogin.as_view(), name='user-login'),

    path('logs/', ListCreateLog.as_view(), name='list-post-errors'),
    path('logs/<str:pk>/', SelectedLog.as_view(), name='get-error'),

    path('users/', GetAllUsers.as_view(), name='list-all-users'),
    path('users/<int:pk>/', UserGetUpdateDelete.as_view(), name='get-user'),
    path('users/<int:pk>/logs/', ListUserAllLogs.as_view(), name='list-user-all-errors')
]

