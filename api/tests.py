from django.test import TestCase
from .models import CustomUser
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .models import Payment
import uuid
from rest_framework.test import APITestCase


# Create your tests here.
class CustomUserModelTest(APITestCase):
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
    def setUp(self):
        # Create a test user
        User = get_user_model()
        self.user = User.objects.create(
            email="test@example.com",
            password=make_password("testpassword123"),
        )

        # Generate JWT token for the user
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        # Add token to client's default headers
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        # Common test data
        self.payment_data = {
            "nonce": "cnon:card-nonce-ok",  # Square's test nonce for successful payments
            "amount": 5000,  # $50.00
            "idempotency_key": str(uuid.uuid4()),
        }

    def test_successful_payment(self):
        """Test a successful payment with valid data"""
        response = self.client.post(
            reverse("payment"), self.payment_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("payment", response.data)
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(Payment.objects.first().status, "SUCCESS")

    def test_unauthorized_request(self):
        """Test payment without authentication"""
        self.client.credentials()  # Remove authentication
        response = self.client.post(
            reverse("payment"), self.payment_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_nonce(self):
        """Test payment with invalid nonce"""
        data = self.payment_data.copy()
        data["nonce"] = "invalid_nonce"
        response = self.client.post(reverse("payment"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_missing_required_fields(self):
        """Test payment with missing required fields"""
        # Test missing nonce
        data = self.payment_data.copy()
        del data["nonce"]
        response = self.client.post(reverse("payment"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test missing amount
        data = self.payment_data.copy()
        del data["amount"]
        response = self.client.post(reverse("payment"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_amount(self):
        """Test payment with invalid amount values"""
        # Test negative amount
        data = self.payment_data.copy()
        data["amount"] = -100
        response = self.client.post(reverse("payment"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test zero amount
        data["amount"] = 0
        response = self.client.post(reverse("payment"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_payment_details(self):
        """Test retrieving payment details"""
        # First create a payment
        response = self.client.post(
            reverse("payment"), self.payment_data, format="json"
        )
        payment_id = response.data["payment"]["payment"]["id"]

        # Then retrieve it
        response = self.client.get(f"{reverse('payment')}?payment_id={payment_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("body", response.data)

    def test_get_invalid_payment(self):
        """Test retrieving non-existent payment"""
        response = self.client.get(f"{reverse('payment')}?payment_id=invalid_id")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_idempotency_key(self):
        """Test duplicate payment with same idempotency key"""
        # Make first payment
        response1 = self.client.post(
            reverse("payment"), self.payment_data, format="json"
        )
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        # Attempt duplicate payment with same idempotency key
        response2 = self.client.post(
            reverse("payment"), self.payment_data, format="json"
        )
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
