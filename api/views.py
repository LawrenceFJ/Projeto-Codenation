from django.shortcuts import render
from rest_framework import generics
from .models import User, ErrorLog
from .serializers import UserSerializer, ErrorLogSerializer

# Create your views here.


class ListErrorsLog(generics.ListAPIView):
    queryset = ErrorLog.objects.all()
    serializer_class = ErrorLogSerializer
