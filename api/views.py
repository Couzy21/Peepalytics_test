from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


# Create your views here.
class PaymentsLiveAPiCheck(APIView):
    def get(request, *args, **kwargs):
        return Response({"message": "Endpoint is live!!!"}, status=status.HTTP_200_OK)
