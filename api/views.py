from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    CustomUserSerializer,
    GenerateTokenSerializer,
    PaymentSerializer,
)
from square.client import Client
from django.conf import settings
from .models import Payment

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


"""
Square payment api
params:source_id: Generated token from the frontend
params: amount to be payed generated from the frontend
params:idempocy_key: Optional
"""


class SquarePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        client = Client(
            access_token=settings.SECRET_ACCESS_TOKEN, environment=settings.ENV
        )
        serialized_data = PaymentSerializer(data=request.data)
        if serialized_data.is_valid():
            payment = Payment.objects.create(
                user=request.user,
                amount=serialized_data.validated_data.get("amount", None),
                status="PENDING",
            )
            body = {
                "source_id": serialized_data.validated_data.get("nonce"),
                "amount_money": {
                    "amount": serialized_data.validated_data.get("amount", None),
                    "currency": settings.DEFAULT_CURRENCY,
                },
                "location_id": settings.SQUARE_LOCATION_ID,
                "idempotency_key": serialized_data.validated_data.get(
                    "idempotency_key"
                ),
                "metadata": payment.id,
            }
            try:
                result = client.payments.create_payment(body)

                if result.is_success():
                    return Response(
                        {"status": "Payment Successful", "payment": result.body},
                        status=status.HTTP_200_OK,
                    )
                elif result.is_error():
                    return Response(
                        {"error": result.errors}, status=status.HTTP_400_BAD_REQUEST
                    )
            except Exception as e:
                return Response(
                    {"message": "payment processing failed", "error": str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            return Response(
                {"message": "Payment successful"}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    "message": "payment processing failed",
                    "error": serialized_data.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class SquarePaymentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({"message": "Payment ID"}, status=status.HTTP_200_OK)
