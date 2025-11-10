from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    PhoneTokenObtainPairView,
    OTPStartView,
    OTPVerifyView,
    ProfileViewSet,
    CredentialsView,
)

router = DefaultRouter()
router.register(r"profiles", ProfileViewSet, basename="profiles")

urlpatterns = [
    # Auth flows
    path("auth/register/", RegisterView.as_view(), name="register"),
    path(
        "auth/token/", PhoneTokenObtainPairView.as_view(), name="token_obtain_pair"
    ),  # password login
    path(
        "auth/otp/start/", OTPStartView.as_view(), name="otp_start"
    ),  # dev OTP -> terminal
    path(
        "auth/otp/verify/", OTPVerifyView.as_view(), name="otp_verify"
    ),  # returns JWTs
    # Profiles & credentials
    path("me/credentials/", CredentialsView.as_view(), name="me_credentials"),
    path("", include(router.urls)),
]
