from django.contrib import admin
from django.urls import path, re_path, include
from .views import ListAllUser, ListCreateErrors, SelectError

urlpatterns = [
    path('errors/', ListCreateErrors.as_view(), name='list-all-errors'),
    path('errors/<int:pk>', SelectError.as_view(), name='get_error'),
    path('users/', ListAllUser.as_view(), name='list-all-users')
]
