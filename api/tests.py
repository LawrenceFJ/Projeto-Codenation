import json
from datetime import datetime, timedelta

from django.urls import reverse

from rest_framework.test import APITestCase, APIClient
from rest_framework.views import status

from .models import User, Agent, ErrorLog
from .serializers import UserSerializer, AgentSerializer, ErrorLogSerializer


# Create your tests here.


class BaseViewTest(APITestCase):
    client = APIClient()

    def setUp(self):
        alexandre = User.objects.create_user(name="alexandre", email="alexandre@gmail.com", password="123465")
        jose = User.objects.create_user(name="jose", email="jose@gmail.com", password="gmmggtes12")
        aline = User.objects.create_user(name="aline", email="aline@gmail.com", password="gmmggtes12")
        kenny = User.objects.create_user(name="kenny", email="kenny@gmail.com", password="gmmggtes12")
        john = User.objects.create_user(name="john", email="john@gmail.com", password="gmmggtes12")
        mario = User.objects.create_user(name="mario", email="mario@gmail.com", password="gmmggtes12")
        maria = User.objects.create_user(name="maria", email="maria@gmail.com", password="gmmggtes12")
        roberto = User.objects.create_user(name="roberto", email="roberto@gmail.com", password="gmmggtes12")
        fabio = User.objects.create_user(name="fabio", email="fabio@gmail.com", password="gmmggtes12")
        denis = User.objects.create_user(name="denis", email="denis@gmail.com", password="gmmggtes12")

        agent_linux = Agent.objects.create(name='linux-server', address='10.0.34.15', status=True, env='production',
                                           version='1.1.1', user=alexandre)
        agent_mac = Agent.objects.create(name='mac-server', address='10.0.34.123', status=True, env='production',
                                         version='1.1.2', user=john)

        ErrorLog.objects.create(level='critical', data=datetime.today(), agent=agent_linux, arquivado=False)
        ErrorLog.objects.create(level='information', data=datetime.today(), agent=agent_mac, arquivado=False)

    def login_a_user(self, email, password):
        return self.client.post(path='/api/login/',
                                data=json.dumps({"email": email,
                                                 "password": password
                                                 }),
                                content_type="application/json"
                                )


###########################################################
################  ERROR LOGS TESTS  #######################
################   URL /api/logs    #######################

class LogsViewTest(BaseViewTest):
    """
        Testes para o /api/logs
    """

    def setUp(self):
        super().setUp()
        user = self.login_a_user(email="alexandre@gmail.com", password="123465")
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
            "level": "warning",
            "agent": 1
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
        log = ErrorLog.objects.filter(level='critical')
        serializer = ErrorLogSerializer(log, many=True)

        response = self.client.get(path='/api/logs/critical/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_put_log(self):
        data = json.dumps({
            "description": "Log de teste updated",
            "details": "Log de teste",
            "level": "warning",
            "agent": 1
        })

        response = self.client.put(path='/api/logs/1/', data=data, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_log(self):
        response = self.client.delete(path='/api/logs/1/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)


###########################################################
################  USER VIEW TESTS  ########################
################  URL /api/users   ########################

class UserViewTest(BaseViewTest):
    """
    Testes para o /api/users
    """

    def setUp(self):
        super().setUp()
        user = self.login_a_user(email="alexandre@gmail.com", password="123465")
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
        response = self.client.delete(path='/api/users/1/', content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)


###########################################################
################  AGENT VIEW TESTS  #######################
################  URL /api/agents/  #######################

class TestAgent(BaseViewTest):
    """
    Testes para /api/agents/
    """
    def setUp(self):
        super().setUp()
        user = self.login_a_user(email="alexandre@gmail.com", password="123465")
        token = 'Bearer ' + user.data['token']
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=token)

    def test_get_all_agents(self):
        agents = Agent.objects.all()
        serializer = AgentSerializer(agents, many=True)

        response = self.client.get(path='/api/agents/', content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_agent_all_logs(self):
        agent = Agent.objects.get(pk=1)
        logs = ErrorLog.objects.filter(agent=agent)
        serializer = ErrorLogSerializer(logs, many=True)

        response = self.client.get(path='/api/agents/1/logs/', content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_post_agent(self):
        agent = json.dumps({
            "name": "windows server",
            "user": 1,
            "address": "10.0.35.35",
            "env": "tests",
            "version": "0.1",
        })

        response = self.client.post(path='/api/agents/', data=agent, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_put_agent(self):
        agent = json.dumps({
            "name": "windows server updated",
            "user": 1,
            "address": "10.0.35.35",
            "env": "tests",
            "version": "0.1",
        })

        response = self.client.put(path='/api/agents/1/', data=agent, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_agent(self):
        response = self.client.delete(path='/api/agents/1/', content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestLoginRegister(BaseViewTest):
    """
    Testes para o /api/register/ e /api/login
    """

    def test_login_valid(self):
        response = self.login_a_user(email="alexandre@gmail.com", password="123465")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_login_invalid_email(self):
        response = self.login_a_user(email='NaoCadastrado@email.com', password="123456")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_login_invalid_password(self):
        response = self.login_a_user(email="alexandre@gmail.com", password="InvalidPassword")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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
        data = {'name': "alexandre", 'email': "alexandre@gmail.com", 'password': "gmmggtes12"}

        response = self.client.post(path=reverse('register-user'), data=data)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
