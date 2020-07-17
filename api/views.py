from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import status
from rest_framework_jwt.settings import api_settings
from django.contrib.auth import authenticate
from django.core.validators import validate_email, ValidationError
from django.shortcuts import render

from .models import User, Agent, ErrorLog
from .serializers import UserSerializer, AgentSerializer, ErrorLogSerializer, TokenSerializer

# Create your views here.


jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


def api_index(request):
    """
    Página de index do site.
    """
    return render(request, 'index.html')


def api_doc(request):
    """
    Página para a documentação da API em swagger.
    """
    return render(request, 'swagger-doc.html')


###########################################################
##################  USER VIEWS  ###########################
###########################################################


class RegisterUser(generics.CreateAPIView):
    """
    POST api/register/
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        email = request.data.get("email", "")
        password = request.data.get("password", "")
        name = request.data.get("name", "")

        try:  # Testa se o email já existe no BD.
            user = User.objects.get(email=email)
            return Response(data={"Message": "User email already exist"}, status=status.HTTP_409_CONFLICT)

        except User.DoesNotExist:
            try:
                validate_email(email)  # Valida o email, se for invalido gera um ValidationError.
                new_user = User.objects.create_user(email=email, password=password, name=name)
                serializer = UserSerializer(new_user)
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)

            except (ValidationError, ValueError):  # ValueError é gerado se a senha for invalida.
                return Response(data={"Message": "User must have an valid email, name and password"},
                                status=status.HTTP_400_BAD_REQUEST)


class UserLogin(generics.CreateAPIView):
    """
    POST api/login/     (user log in)
    """
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        try:  # Testa se o usuario existe no BD.
            user = self.queryset.get(email=request.data['email'])
        except User.DoesNotExist:
            return Response(data={'Message': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

        email = request.data['email']
        password = request.data['password']
        user = authenticate(request, username=email, password=password)  # Validação do usuario.

        # Se o usuario for valido, retorna o token.
        if user is not None:
            serializer = TokenSerializer(data={
                "token": jwt_encode_handler(
                    jwt_payload_handler(user)
                )})
            serializer.is_valid()
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        return Response(data={'Message': 'Invalid Password'}, status=status.HTTP_400_BAD_REQUEST)


class GetAllUsers(generics.ListAPIView):
    """
    GET api/users/
    Retorna todos os usuario cadastrados.
    """
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserGetUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    """
    GET api/users/:id/
    PUT api/users/:id/
    DELETE api/users/:id/
    """
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        """
        Retorna o usuario com id buscado.
        :param request:
        :param args:
        :param kwargs:
        :return User[]:
        """
        try:
            a_user = User.objects.get(pk=kwargs['pk'])
            serializer = UserSerializer(a_user)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                data={"Message": f"User with id={kwargs['pk']} does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, *args, **kwargs):
        """
        Atualização das informações de um Usuario.
        Retorna o usuario atualizado.
        :param request:
        :param args:
        :param kwargs:
        :return User[]:
        """
        try:  # verifica se o usuario existe no banco.
            a_user = self.queryset.get(pk=kwargs['pk'])

            try:    # verifica se no json tem o campo email. Se não estiver, raise KeyError.
                validate_email(request.data['email'])   # valida o email do json. Se for invalido, raise ValidationError
            except KeyError:
                pass

            # verifica se o name não contem letras, ex: name="   ".
            if not request.data['name'].strip():
                raise ValueError

            serializer = UserSerializer()
            serializer.update(a_user, request.data)
            updated_user = self.queryset.get(pk=kwargs['pk'])
            serializer = UserSerializer(updated_user)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except (User.DoesNotExist, ValueError, ValidationError) as e:
            if e is ValueError or ValidationError:
                return Response(data={"Message": "Invalid email or name"}, status=status.HTTP_400_BAD_REQUEST)
            return Response(
                data={"Message": f"User with id={kwargs['pk']} does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, *args, **kwargs):
        """
        Deleta o Usuário pelo id.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            a_user = self.queryset.get(pk=kwargs['pk'])
            a_user.delete()
            return Response(status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                data={"Message": f"User with id={kwargs['pk']} does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

###########################################################
###################  AGENT VIEWS  #########################
###########################################################


class ListCreateAgent(generics.ListCreateAPIView):
    """
    GET api/agents
    POST api/agents
    """
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer

    def post(self, request, *args, **kwargs):
        """
        Registra um Agent no BD.
        Retorna o Agent criado.
        :param request:
        :param args:
        :param kwargs:
        :return Agent[]:
        """
        serializer = AgentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetUpdateDeleteAgent(generics.RetrieveUpdateDestroyAPIView):
    """
    GET api/agents/:id/
    PUT api/agents/:id/
    DELETE api/agents/:id/
    """
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer

    def get(self, request, *args, **kwargs):
        """
        Busca um Agent com o determinado ID.
        Retorna o Agent buscado.
        :param request:
        :param args:
        :param kwargs:
        :return Agent[]:
        """
        try:
            a_agent = self.queryset.get(pk=kwargs['pk'])
            return Response(AgentSerializer(a_agent).data)
        except (Agent.DoesNotExist, ValueError):
            return Response(
                data={"Message": f"Agent with id={kwargs['pk']} does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, *args, **kwargs):
        """
        Atualiza um Agent determinado pelo ID.
        Retorna o Agent atualizado.
        :param request:
        :param args:
        :param kwargs:
        :return Agent[]:
        """
        try:
            a_agent = self.queryset.get(pk=kwargs['pk'])
            serializer = AgentSerializer()

            try:
                a_user = User.objects.get(pk=request.data['user'])
                request.data['user'] = a_user
            except KeyError:
                pass

            updated_error = serializer.update(a_agent, request.data)
            return Response(data=AgentSerializer(updated_error).data, status=status.HTTP_200_OK)
        except Agent.DoesNotExist:
            return Response(
                data={"Message": f"Agent with id={kwargs['pk']} does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, *args, **kwargs):
        """
        Deleta um Agent selecionado pelo ID.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            a_agent = self.queryset.get(pk=kwargs['pk'])
            a_agent.delete()
            return Response(status=status.HTTP_200_OK)
        except Agent.DoesNotExist:
            return Response(
                data={"Message": f"Agent with id={kwargs['pk']} does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )


class ListAgentAllLogs(generics.ListAPIView):
    """
    GET api/agents/:id/logs
    """
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ErrorLog.objects.all()
    serializer_class = ErrorLogSerializer

    def get(self, request, *args, **kwargs):
        """
        Lista todos os Logs criados pelo Agent determinado pelo ID.
        Retorna a lista de Logs.
        :param request:
        :param args:
        :param kwargs:
        :return ErrorLog[]:
        """
        query = self.queryset.filter(agent=kwargs['pk'])
        serializer = ErrorLogSerializer(query, many=True)
        if query:
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            data={"Message": f"This agent does not have logs entries."},
            status=status.HTTP_404_NOT_FOUND
        )


###########################################################
################  ERROR LOGS VIEWS  #######################
###########################################################


class ListCreateLog(generics.ListCreateAPIView):
    """
    GET api/logs/
    POST api/logs/
    """
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ErrorLog.objects.all()
    serializer_class = ErrorLogSerializer

    def post(self, request, *args, **kwargs):
        """
        Registra um Log no BD.
        Retorna o Log criado.
        :param request:
        :param args:
        :param kwargs:
        :return ErrorLog[]:
        """
        serializer = ErrorLogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetUpdateDeleteLog(generics.RetrieveUpdateDestroyAPIView):
    """
    GET api/logs/:id/
    GET api/logs/:level/

    PUT api/logs/:id/
    DELETE api/logs/:id/
    """
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ErrorLog.objects.all()
    serializer_class = ErrorLogSerializer

    def get(self, request, *args, **kwargs):
        """
        Se buscado pelo ID, retorna o Log especifico. Se buscado pelo level, retorna todos os Logs com aquele level.
        :param request:
        :param args:
        :param kwargs:
        :return ErrorLog[]:
        """
        LEVEL_CHOICES = ['critical', 'debug', 'error', 'warning', 'information']

        # GET errors/:level/
        if kwargs['pk'] in LEVEL_CHOICES:  # kwargs['pk'] é um level_choice.
            a_error = self.queryset.filter(level=kwargs['pk'])
            serializer = ErrorLogSerializer(a_error, many=True)
            if not a_error:
                return Response(
                    data={"Message": f"Errors with level:{kwargs['pk']} does not have entries."},
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response(serializer.data)

        # GET errors/:id/
        else:  # kwargs['pk'] é um numero.
            try:
                a_error = self.queryset.get(pk=kwargs['pk'])
                return Response(ErrorLogSerializer(a_error).data)
            except (ErrorLog.DoesNotExist, ValueError):
                return Response(
                    data={"Message": f"Error Log id={kwargs['pk']} does not exist."},
                    status=status.HTTP_404_NOT_FOUND
                )

    def put(self, request, *args, **kwargs):
        """
        Atualiza um Log especificado pelo ID.
        Retorna o Log atualizado.
        :param request:
        :param args:
        :param kwargs:
        :return ErrorLog[]:
        """
        try:
            a_error = self.queryset.get(pk=kwargs['pk'])
            serializer = ErrorLogSerializer()

            try:
                a_agent = Agent.objects.get(pk=request.data['agent'])
                request.data['agent'] = a_agent
            except KeyError:
                pass

            updated_error = serializer.update(a_error, request.data)
            return Response(data=ErrorLogSerializer(updated_error).data, status=status.HTTP_200_OK)
        except ErrorLog.DoesNotExist:
            return Response(
                data={"Message": f"Error Log id={kwargs['pk']} does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, *args, **kwargs):
        """
        Delete um Log especificado pelo ID.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:
            a_error = self.queryset.get(pk=kwargs['pk'])
            a_error.delete()
            return Response(status=status.HTTP_200_OK)
        except ErrorLog.DoesNotExist:
            return Response(
                data={"Message": f"Error Log id={kwargs['pk']} does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )
