from django.urls import path

from .views import PaymentsLiveAPiCheck

urlpatterns = [
    path("", PaymentsLiveAPiCheck.as_view(), name="live_check"),
]
