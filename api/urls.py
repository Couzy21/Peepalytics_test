from django.urls import path

from .views import PaymentsLiveAPiCheck, LoginView, UserRegistrationView

urlpatterns = [
    path("", PaymentsLiveAPiCheck.as_view(), name="live_check"),
    path("signup/", UserRegistrationView.as_view(), name="Signup"),
    path("login/", LoginView.as_view(), name="login"),
]
