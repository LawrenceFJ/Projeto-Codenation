import json
from datetime import datetime

from django.urls import reverse

from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status

from .models import User, ErrorLog
from .serializers import UserSerializer, ErrorLogSerializer


# Create your tests here.


class BaseViewTest(APITestCase):
    client = APIClient()

    def setUp(self):
        self.joao = User.objects.create_user(email='Joao@email.com', name='Joao', password="123456")
        carlos = User.objects.create_user(email='Carlos@email.com', name='Carlos', password="456789")
        ErrorLog.objects.create(description='Erro Teste', details='Cadastro de um erro para teste',
                                origin='192.168.100.50', date=datetime.now(), level='warning', user=self.joao)
        ErrorLog.objects.create(description='Erro Teste n2', details='Cadastro de um erro para teste n2',
                                origin='192.168.100.100', date=datetime.now(), level='error', user=carlos)

    def login_a_user(self, email="", name="", password=""):
        url = reverse("user-login")
        return self.client.post(
            url,
            data=json.dumps({
                "email": email,
                "name": name,
                "password": password
            }),
            content_type="application/json"
        )


class LogsViewTest(BaseViewTest):
    def setUp(self):
        super().setUp()
        user = self.login_a_user(email='Joao@email.com', name='Joao', password="123456")
        token = 'Bearer ' + user.data['token']
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=token)

    def test_get_all_Logs(self):
        logs = ErrorLog.objects.all()
        serializer = ErrorLogSerializer(logs, many=True)

        response = self.client.get('/api/logs/')

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_log(self):
        data = json.dumps({
            "description": "Log de teste",
            "details": "Log de teste",
            "origin": "127.0.0.1",
            "date": "2020-11-11 11:11:11",
            "level": "warning",
            "user": 1
        })
        response = self.client.post('/api/logs/', data=data, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_specific_log_by_id(self):
        log = ErrorLog.objects.get(id=1)
        serializer = ErrorLogSerializer(log)

        response = self.client.get('/api/logs/1/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_specific_log_by_level(self):
        log = ErrorLog.objects.filter(level='error')
        serializer = ErrorLogSerializer(log, many=True)

        response = self.client.get(path='/api/logs/error/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_put_log(self):
        data = json.dumps({
            "description": "Log de teste",
            "details": "Log de teste",
            "origin": "127.0.0.1",
            "date": "2020-11-11 11:11:11",
            "level": "warning",
            "user": 1
        })

        response = self.client.put(path='/api/logs/1/', data=data, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_log(self):
        response = self.client.delete(path='/api/logs/1/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserViewTest(BaseViewTest):
    """
    Testes para o /api/users
    """
    def setUp(self):
        super().setUp()
        user = self.login_a_user(email='Joao@email.com', name='Joao', password="123456")
        token = 'Bearer ' + user.data['token']
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=token)

    def test_get_all_users(self):
        """
        Test GET /api/users
        """
        user = User.objects.all()
        serializer = UserSerializer(user, many=True)

        response = self.client.get('/api/users/')

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_specific_user_by_id(self):
        """
        Test GET /api/users/:id/
        """
        user = User.objects.get(id=1)
        serializer = UserSerializer(user)

        response = self.client.get('/api/users/1/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_logs_by_user(self):
        """
        Test GET /api/users/:id/logs
        """
        user = User.objects.get(id=1)
        log = ErrorLog.objects.filter(user=user)
        serializer = ErrorLogSerializer(log, many=True)

        response = self.client.get(path='/api/users/1/logs/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_put_user(self):
        """
        Test PUT /api/users/:id
        """
        data = json.dumps({
            "email": "Carlos2@email.com",
            "name": "Carlos2",
        })

        response = self.client.put(path='/api/users/2/', data=data, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put_user_invalid_email(self):
        """
        Test PUT /api/users/:id with a invalid email
        """
        data = json.dumps({
            "email": "Invalid Email"
        })

        response = self.client.put(path='/api/users/2/', data=data, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_put_user_blank_name(self):
        """
        Test PUT /api/users/:id with a invalid name
        """
        data = json.dumps({
            "name": "    "
        })

        response = self.client.put(path='/api/users/2/', data=data, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_user(self):
        """
        Test DELETE /api/users/:id
        """
        response = self.client.delete(path='/api/users/2/', content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestLogin(BaseViewTest):
    """
    Testes para o /api/login/
    """
    def test_login_valid(self):
        response = self.login_a_user(email='Joao@email.com', password="123456")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_login_invalid_email(self):
        response = self.login_a_user(email='NaoCadastrado@email.com', password="123456")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_login_invalid_password(self):
        response = self.login_a_user(email='Joao@email.com', password="Invalid password")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TestRegister(BaseViewTest):
    """
    Testes para o /api/register/
    """
    def test_register_valid_user(self):
        data = {'email': 'Emanuel@email.com', 'name': 'Emanuel', 'password': '123456'}

        response = self.client.post(path=reverse('register-user'), data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_invalid_user_email(self):
        data = {'email': 'Invalid Email', 'name': 'Emanuel', 'password': '123456'}

        response = self.client.post(path=reverse('register-user'), data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_invalid_user_password(self):
        data = {'email': 'Emanuel@email.com', 'name': 'Emanuel', 'password': ''}

        response = self.client.post(path=reverse('register-user'), data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_invalid_user_name(self):
        data = {'email': 'Emanuel@email.com', 'name': '', 'password': '123456'}

        response = self.client.post(path=reverse('register-user'), data=data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_already_exist(self):
        data = {'email': 'Joao@email.com', 'name': 'Joao', 'password': '123456'}

        response = self.client.post(path=reverse('register-user'), data=data)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
