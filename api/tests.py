from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status
from .models import User, ErrorLog
from .serializers import UserSerializer, ErrorLogSerializer
from datetime import datetime


# Create your tests here.


class BaseViewTest(APITestCase):
    client = APIClient()

    def setUp(self):
        joao = User.objects.create(email='Joao@email.com', password="123456")
        carlos = User.objects.create(email='Carlos@email.com', password="456789")
        ErrorLog.objects.create(description='Erro Teste', details='Cadastro de um erro para teste',
                                origin='192.168.100.50', date=datetime.now(), level='warning', user=joao)
        ErrorLog.objects.create(description='Erro Teste n2', details='Cadastro de um erro para teste n2',
                                origin='192.168.100.100', date=datetime.now(), level='error', user=carlos)


class GetAllErrors(BaseViewTest):
    def test_get_all_errors(self):
        response = self.client.get(reverse('get-all-errors'))
        expect = ErrorLog.objects.all()
        serialized = ErrorLogSerializer(expect, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)