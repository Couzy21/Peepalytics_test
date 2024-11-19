from django.test import TestCase, APITestCase
from .models import CustomUser
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from rest_framework import status


# Create your tests here.
class CustomUserModelTest(TestCase):
    def test_create_user_successfull(self):
        user = CustomUser.objects.create(
            name="John Doe",
            email="johndoe@testexample.com",
            password=make_password("testpassword123"),
        )

        self.assertEqual(user.email, "johndoe@testexample.com")
        self.assertEqual(
            user.username, "johndoe@testexample.com"
        )  # Ensure the username is set to the email
        self.assertTrue(
            user.check_password("testpassword123")
        )  # Check if the password is set correctly

        self.assertEqual(user.name, "John Doe")
        self.assertTrue(user.is_active)


class SquarePaymentEndpointTest(APITestCase):
    def test_valid_payment_request(self):
        data = {
            "nonce": "cnon_test_1234567890",
            "amount": 5000,
            "idempotency_key": "unique_key_123456",
        }
        response = self.client.post(reverse("payment"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("status", response.data)

    def test_invalid_nonce(self):
        data = {
            "nonce": "invalid_nonce",
            "amount": 5000,
            "idempotency_key": "unique_key_123456",
        }
        response = self.client.post(reverse("square-payment"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("nonce", response.data)
