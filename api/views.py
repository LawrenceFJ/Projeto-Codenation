from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import status
from rest_framework_jwt.settings import api_settings
from django.contrib.auth import authenticate

from .models import User, ErrorLog
from .serializers import UserSerializer, ErrorLogSerializer, TokenSerializer


# Create your views here.


jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

###########################################################
##################  USER VIEWS  ###########################
###########################################################


class RegisterUser(generics.CreateAPIView):
    """
    POST register/
    """
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        if request.data['passcode'] == 'True':
            return Response(data={'Message': 'Successfully Registered',
                                  'Email': request.data['email']},
                            status=status.HTTP_201_CREATED)
        return Response(data={'Message': 'Invalid Passcode'}, status=status.HTTP_400_BAD_REQUEST)


class UserLogin(generics.CreateAPIView):
    """
    POST login/     (user log in)
    """
    permission_classes = (permissions.AllowAny, )
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        try:
            email = request.data['email']
            password = request.data['password']
            user = authenticate(request, username=email, password=password)
            if user:
                try:
                    serializer = TokenSerializer(data={
                        "token": jwt_encode_handler(
                            jwt_payload_handler(user)
                        )})
                    serializer.is_valid()
                    return Response(data=serializer.data)
                except Exception as e:
                    raise e
        except User.DoesNotExist:
            return Response(data={'Message': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)


class GetAllUsers(generics.ListAPIView):
    """
    GET users/
    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserGetUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    """
    GET users/:id/
    PUT users/:id/
    DELETE users/:id/
    """
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        try:
            a_user = User.objects.get(pk=kwargs['pk'])
            serializer = UserSerializer(a_user)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response(
                data={"Message": f"User with id={kwargs['pk']} does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, *args, **kwargs):
        try:
            a_user = self.queryset.get(pk=kwargs['pk'])
            serializer = ErrorLogSerializer()
            updated_user = serializer.update(a_user, request.data)
            return Response(updated_user)
        except User.DoesNotExist:
            return Response(
                data={"Message": f"User with id={kwargs['pk']} does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, *args, **kwargs):
        try:
            a_user = self.queryset.get(pk=kwargs['pk'])
            a_user.delete()
        except User.DoesNotExist:
            return Response(
                data={"Message": f"User with id={kwargs['pk']} does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )


class ListUserAllLogs(generics.ListAPIView):
    """
    GET users/:id/logs
    """
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ErrorLog.objects.all()
    serializer_class = ErrorLogSerializer

    def get(self, request, *args, **kwargs):
        query = self.queryset.filter(user=kwargs['pk'])
        serializer = ErrorLogSerializer(query, many=True)
        if query:
            return Response(serializer.data)
        return Response(
            data={"Message": f"User with id={kwargs['pk']} does not exist."},
            status=status.HTTP_404_NOT_FOUND
        )


###########################################################
################  ERROR LOGS VIEWS  #######################
###########################################################


class ListCreateLog(generics.ListCreateAPIView):
    """
    GET logs/
    POST logs/
    """
    permission_classes = (permissions.IsAuthenticated, )
    queryset = ErrorLog.objects.all()
    serializer_class = ErrorLogSerializer

    def post(self, request, *args, **kwargs):
        serializer = ErrorLogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SelectedLog(generics.RetrieveUpdateDestroyAPIView):
    """
    GET logs/:id/
    GET logs/:level/

    PUT logs/:id/
    DELETE logs/:id/
    """
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ErrorLog.objects.all()
    serializer_class = ErrorLogSerializer

    def get(self, request, *args, **kwargs):
        LEVEL_CHOICES = ['critical', 'debug', 'error', 'warning', 'information']

        # GET errors/:level/
        if kwargs['pk'] in LEVEL_CHOICES:
            a_error = self.queryset.filter(level=kwargs['pk'])
            serializer = ErrorLogSerializer(a_error, many=True)
            if not a_error:
                return Response(
                    data={"Message": f"Errors with level:{kwargs['pk']} does not have entries."},
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response(serializer.data)

        # GET errors/:id/
        else:  # kwargs['pk'] is a number
            try:
                a_error = self.queryset.get(pk=kwargs['pk'])
                return Response(ErrorLogSerializer(a_error).data)
            except (ErrorLog.DoesNotExist, ValueError):
                return Response(
                    data={"Message": f"Error Log id={kwargs['pk']} does not exist."},
                    status=status.HTTP_404_NOT_FOUND
                )

    def put(self, request, *args, **kwargs):
        try:
            a_error = self.queryset.get(pk=kwargs['pk'])
            serializer = ErrorLogSerializer()

            a_user = User.objects.get(pk=request.data['user'])
            request.data['user'] = a_user

            updated_error = serializer.update(a_error, request.data)
            return Response(data=ErrorLogSerializer(updated_error).data, status=status.HTTP_200_OK)
        except ErrorLog.DoesNotExist:
            return Response(
                data={"Message": f"Error Log id={kwargs['pk']} does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, *args, **kwargs):
        try:
            a_error = self.queryset.get(pk=kwargs['pk'])
            a_error.delete()
            return Response(status=status.HTTP_200_OK)
        except ErrorLog.DoesNotExist:
            return Response(
                data={"Message": f"Error Log id={kwargs['pk']} does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )
