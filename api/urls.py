from django.contrib import admin
from django.urls import path, re_path, include
from .views import ListErrorsLog

urlpatterns = [
    path('errors-log/', ListErrorsLog.as_view(), name='get-all-errors')
]
