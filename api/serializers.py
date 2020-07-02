from rest_framework import serializers
from .models import User, ErrorLog


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password')


class ErrorLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorLog
        fields = ('id', 'description', 'details', 'origin', 'date', 'level', 'user')
