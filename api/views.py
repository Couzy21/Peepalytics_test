from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .serializers import (
    CustomUserSerializer,
    GenerateTokenSerializer,
    PaymentSerializer,
)
from square.client import Client
from square.api.payments_api import PaymentsApi
from django.conf import settings
from .models import Payment
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

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
Square payment API
#POST
Used to create a new payment on square
params:source_id: Generated token from the frontend
params: amount to be payed generated from the frontend
params:idempocy_key: Optional
#GET
params: payment_id: Passed in the GET request to fetch a particular transaction
"""


class SquarePaymentView(APIView):
    permission_classes = [IsAuthenticated]
    client = Client(access_token=settings.SQUARE_ACCESS_TOKEN, environment=settings.ENV)

    def get(self, request, *args, **kwargs):
        try:
            payment_id = request.GET.get("payment_id", None)
            if payment_id:
                result = self.client.payments.get_payment(payment_id=payment_id)

            if result.is_success():
                return Response(
                    {"message": "success", "body": result.body.get("payment", None)},
                    status=status.HTTP_200_OK,
                )
            elif result.is_error():
                return Response(
                    {"message": "an error occured", "error": result.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {"message": "an error occured", "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def post(self, request):
        serialized_data = PaymentSerializer(data=request.data)
        if serialized_data.is_valid():
            # Reverse database transactions in case of failure
            with transaction.atomic():
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
                    "idempotency_key": serialized_data.validated_data.get(
                        "idempotency_key"
                    ),
                    "reference_id": str(payment.id),
                }
                try:
                    result = self.client.payments.create_payment(body)

                    if result.is_success():
                        payment.status = "SUCCESS"
                        result = result.body
                        payment_data = result.get("payment", None)
                        payment.payment_id = payment_data["id"]
                        payment.save()
                        return Response(
                            {"message": "Payment Successful", "payment": result},
                            status=status.HTTP_200_OK,
                        )
                    elif result.is_error():
                        payment.status = "FAILED"
                        payment.save()
                        return Response(
                            {
                                "message": "an error occured while processing payment request",
                                "error": result.errors,
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                except Exception as e:
                    return Response(
                        {"message": "payment processing failed", "error": str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
        else:
            return Response(
                {
                    "message": "payment processing failed",
                    "error": serialized_data.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


# webhook to update database with payment status after successful payment
@method_decorator(csrf_exempt, name="dispatch")
class SquareWebhookView(APIView):
    def post(self, request):
        event_data = request.data
        if "type" in event_data and event_data["type"] == "payment.updated":
            payment_id = event_data["data"]["object"]["payment"]["reference_id"]
            status = event_data["data"]["object"]["payment"]["status"]

            try:
                payment = Payment.objects.get(id=payment_id)
                if status == "COMPLETED":
                    payment.status = "SUCCESS"
                elif status == "FAILED":
                    payment.status = "FAILED"
                payment.save()
                return Response(
                    {"message": "Payment status updated successfully"},
                    status=status.HTTP_200_OK,
                )
            except Payment.DoesNotExist:
                return Response(
                    {"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND
                )

        return Response(
            {"message": "Event not processed"}, status=status.HTTP_400_BAD_REQUEST
        )
