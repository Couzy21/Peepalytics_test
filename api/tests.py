from django.test import TestCase
from .models import CustomUser
from django.contrib.auth.hashers import make_password


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
