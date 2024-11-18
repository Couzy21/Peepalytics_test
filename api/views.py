from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from .serializers import CustomUserSerializer, GenerateTokenSerializer


# Create your views here.
"""
Endpoint for liveness check
"""


class PaymentsLiveAPiCheck(APIView):
    permission_classes = []

    def get(request, *args, **kwargs):
        return Response({"message": "Endpoint is live!!!"}, status=status.HTTP_200_OK)


class UserRegistrationView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                user.save()
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "email": user.email,
                    "message": "User registered",
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    serializer_class = GenerateTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )


class SquarePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({"message": "Payment successful"}, status=status.HTTP_200_OK)


class SquarePaymentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({"message": "Payment ID"}, status=status.HTTP_200_OK)
