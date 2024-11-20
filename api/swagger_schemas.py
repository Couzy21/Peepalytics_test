from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .serializers import CustomUserSerializer, PaymentSerializer

# Liveness Check
liveness_check_schema = swagger_auto_schema(
    operation_description="Endpoint for liveness check",
    responses={200: openapi.Response(description="Endpoint is live")},
)

# User Registration
user_registration_schema = swagger_auto_schema(
    operation_description="Register a new user",
    request_body=CustomUserSerializer,
    responses={
        201: openapi.Response(
            description="User registered successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "refresh": openapi.Schema(type=openapi.TYPE_STRING),
                    "access": openapi.Schema(type=openapi.TYPE_STRING),
                    "email": openapi.Schema(type=openapi.TYPE_STRING),
                    "message": openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
        ),
        400: "Bad Request",
    },
)

# Square Payment
square_payment_get_schema = swagger_auto_schema(
    operation_description="Fetch payment details from Square",
    manual_parameters=[
        openapi.Parameter(
            "payment_id",
            openapi.IN_QUERY,
            description="Square payment ID",
            type=openapi.TYPE_STRING,
            required=True,
        )
    ],
    responses={
        200: "Payment details retrieved successfully",
        400: "Bad request or payment fetch failed",
    },
)

square_payment_post_schema = swagger_auto_schema(
    operation_description="Create a new payment using Square",
    request_body=PaymentSerializer,
    responses={
        200: "Payment processed successfully",
        400: "Bad request or payment processing failed",
        500: "Internal server error",
    },
)

# Square Webhook
square_webhook_schema = swagger_auto_schema(
    operation_description="Webhook endpoint for Square payment status updates",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "type": openapi.Schema(type=openapi.TYPE_STRING),
            "data": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "object": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "payment": openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "reference_id": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "status": openapi.Schema(type=openapi.TYPE_STRING),
                                },
                            )
                        },
                    )
                },
            ),
        },
    ),
    responses={
        200: "Payment status updated successfully",
        400: "Event not processed",
        404: "Payment not found",
    },
)
