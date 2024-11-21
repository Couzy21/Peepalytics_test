from django.urls import path

from .views import (
    PaymentsLiveAPiCheck,
    LoginView,
    UserRegistrationView,
    SquarePaymentView,
    PaymentListCreateAPIView,
)

urlpatterns = [
    path("", PaymentsLiveAPiCheck.as_view(), name="live_check"),
    path("signup/", UserRegistrationView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("payment/", SquarePaymentView.as_view(), name="payment"),
    path("payments-list/", PaymentListCreateAPIView.as_view(), name="payments-list"),
]
