from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status
from .models import User, ErrorLog
from .serializers import UserSerializer, ErrorLogSerializer


# Create your views here.

###########################################################
##################  USER VIEWS  ###########################
###########################################################


class ListAllUser(generics.ListAPIView):
    """
    GET users/
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


###########################################################
################  ERROR LOGS VIEWS  #######################
###########################################################


class ListCreateErrors(generics.ListAPIView):
    """
    GET errors/
    POST errors/
    """
    queryset = ErrorLog.objects.all()
    serializer_class = ErrorLogSerializer

    def post(self, request, *args, **kwargs):
        serializer = ErrorLogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SelectError(generics.ListAPIView):
    """
    GET errors/:id/
    PUT errors/:id/
    DELETE errors/:id/
    """
    queryset = ErrorLog.objects.all()
    serializer_class = ErrorLogSerializer

    def get(self, request, *args, **kwargs):
        try:
            a_error = self.queryset.get(pk=kwargs['pk'])
            return Response(ErrorLogSerializer(a_error).data)
        except ErrorLog.DoesNotExist:
            return Response(
                data={"message": f"Error Log id={kwargs['pk']} does not exist."},
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
                data={"message": f"Error Log id={kwargs['pk']} does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, *args, **kwargs):
        try:
            a_error = self.queryset.get(pk=kwargs['pk'])
            a_error.delete()
            return Response(status=status.HTTP_200_OK)
        except ErrorLog.DoesNotExist:
            return Response(
                data={"message": f"Error Log id={kwargs['pk']} does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )
