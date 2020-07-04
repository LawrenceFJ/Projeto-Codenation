from django.contrib import admin
from django.urls import path, re_path, include
from .views import ListAllUser, SelectedUser, ListUserAllErrors, ListCreateErrors, SelectedError

urlpatterns = [
    path('errors/', ListCreateErrors.as_view(), name='list-all-errors'),
    path('errors/<str:pk>/', SelectedError.as_view(), name='get-error'),
    path('users/', ListAllUser.as_view(), name='list-all-users'),
    path('users/<int:pk>/', SelectedUser.as_view(), name='get-user'),
    path('users/<int:pk>/errors/', ListUserAllErrors.as_view(), name='list-user-all-errors')
]
