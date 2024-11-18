from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    # Add addtional fields here
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(_("active"), default=True)
    date_joined = models.DateTimeField(_("date_joined"), auto_now_add=True)

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        # Ensures the email is stored in lowercase
        self.email = self.email.lower()

        # Automatically populates the username field with the email
        if not self.username:
            self.username = self.email

        super().save(*args, **kwargs)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]


class Payment(models.Model):
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, db_index=True, default=1
    )

    def __str__(self):
        return f"{self.user} created payment of {self.amount}"
