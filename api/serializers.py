from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from rest_framework.validators import UniqueValidator
from .models import CustomUser

"""
Serializer for authenticating user login through JWT token provider
"""


class GenerateTokenSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(default=None, required=False)
    password = serializers.CharField()
    username = serializers.CharField(default=None)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        username = attrs.get("username", None)

        if email and password:
            user = authenticate(
                request=self.context.get("request"),
                username=username,
                email=email,
                password=password,
            )
            if not user:
                raise serializers.ValidationError(
                    "Unable to log in with provided credentials."
                )

        else:
            raise serializers.ValidationError("Must include 'email' and 'password'.")

        attrs["user"] = user
        return attrs

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if "user" not in representation:
            error_message = representation.get(
                "non_field_errors", ["Unable to log in with provided credentials."]
            )[0]
            # print(f"Error: {error_message}")
        return representation


class CustomUserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(
        required=True, validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )

    class Meta:
        model = CustomUser
        fields = ("id", "name", "email", "password")

    def create(self, validated_data):
        # Hash the password before saving
        validated_data["password"] = make_password(validated_data["password"])

        return super().create(validated_data)


class PaymentSerializer(serializers.Serializer):
    nonce = serializers.CharField(max_length=255, required=True)
    amount = serializers.IntegerField(min_value=1, required=True)
    idempotency_key = serializers.CharField(max_length=255, required=True)

    def validate_idempotency_key(self, value):
        # Ensure the idempotency key is unique or has a specific format
        if len(value) < 10:  # Example: minimum length check
            raise serializers.ValidationError("Idempotency key is too short.")
        return value
