from django.urls import path

from .views import (
    PaymentsLiveAPiCheck,
    LoginView,
    UserRegistrationView,
    SquarePaymentView,
    SquarePaymentDetailView,
)

urlpatterns = [
    path("", PaymentsLiveAPiCheck.as_view(), name="live_check"),
    path("signup/", UserRegistrationView.as_view(), name="Signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("payment/", SquarePaymentView.as_view(), name="payment"),
    path("payment/<int>/", SquarePaymentDetailView.as_view(), name="payment-details"),
]
