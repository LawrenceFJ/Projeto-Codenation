from rest_framework import serializers
from .models import User, ErrorLog


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password')


class ErrorLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorLog
        fields = ('description', 'details', 'origin', 'date', 'level', 'user')
