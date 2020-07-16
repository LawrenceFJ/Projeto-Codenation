from django.urls import path, re_path, include
from .views import RegisterUser, UserLogin, GetAllUsers, UserGetUpdateDelete
from .views import ListCreateLog, GetUpdateDeleteLog
from .views import ListCreateAgent, GetUpdateDeleteAgent, ListAgentAllLogs

urlpatterns = [
    path('api/register/', RegisterUser.as_view(), name='register-user'),
    path('api/login/', UserLogin.as_view(), name='user-login'),

    path('api/logs/', ListCreateLog.as_view(), name='list-post-errors'),
    path('api/logs/<str:pk>/', GetUpdateDeleteLog.as_view(), name='get-error'),

    path('api/users/', GetAllUsers.as_view(), name='list-all-users'),
    path('api/users/<int:pk>/', UserGetUpdateDelete.as_view(), name='get-user'),

    path('api/agents/', ListCreateAgent.as_view(), name='list-all-agents'),
    path('api/agents/<int:pk>/', GetUpdateDeleteAgent.as_view(), name='get-agent'),
    path('api/agents/<int:pk>/logs/', ListAgentAllLogs.as_view(), name='get-agent-all-logs'),
]

