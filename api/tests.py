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
        response = self.client.get(reverse('list-post-errors'))
        expect = ErrorLog.objects.all()
        serialized = ErrorLogSerializer(expect, many=True)
        self.assertEqual(response.data, serialized.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestLogin(BaseViewTest):
    def test_login_valid(self):
        data = {'email': 'Joao@email.com', 'password': "123456"}

        response = self.client.post(path=reverse('user-login'), data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_invalid(self):
        data = {'email': 'invalidemail@email.com', 'password': 'invalidpassword'}

        response = self.client.post(path=reverse('user-login'), data=data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class TestRegister(APITestCase):
    """
    Testes para o register/
    """
    def test_register_valid_data(self):
        data = {'email': 'Emanuel@email.com', 'name': 'Emanuel', 'password': '123456'}
        response = self.client.post(path=reverse('register-user'), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_invalid_data(self):
        data = {'email': '', 'name': 'Emanuel', 'password': '123456'}
        response = self.client.post(path=reverse('register-user'), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
