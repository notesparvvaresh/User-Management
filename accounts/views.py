import random
import logging
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import generics, permissions, status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    RegisterSerializer,
    ProfileSerializer,
    ProfileUpdateSerializer,
    CredentialsUpdateSerializer,
    OTPStartSerializer,
    OTPVerifySerializer,
)
from .models import Profile

logger = logging.getLogger(__name__)
User = get_user_model()


# ---- JWT with phone_number (password-based) ----
class PhoneTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["phone_number"] = user.phone_number
        return token

    def validate(self, attrs):
        # Map "phone_number" to expected "username" field
        if "phone_number" in self.initial_data and "username" not in attrs:
            attrs["username"] = self.initial_data.get("phone_number")
        return super().validate(attrs)


class PhoneTokenObtainPairView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PhoneTokenObtainPairSerializer


# ---- OTP (prints to terminal) ----


def _otp_key(phone: str) -> str:
    return f"otp:{phone}"


class OTPStartView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = OTPStartSerializer

    def post(self, request):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        phone = s.validated_data["phone_number"]
        otp = f"{random.randint(0, 999999):06d}"
        cache.set(_otp_key(phone), otp, timeout=300)  # 5 minutes
        logger.warning("DEV OTP for %s is %s", phone, otp)  # shows in terminal
        return Response(
            {"detail": "OTP generated (check server terminal)."}, status=200
        )


class OTPVerifyView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = OTPVerifySerializer

    def post(self, request):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        phone = s.validated_data["phone_number"]
        otp = s.validated_data["otp"]
        expected = cache.get(_otp_key(phone))
        if not expected or expected != otp:
            return Response({"detail": "Invalid OTP."}, status=400)
        cache.delete(_otp_key(phone))
        user, _ = User.objects.get_or_create(phone_number=phone)
        refresh = RefreshToken.for_user(user)
        return Response(
            {"access": str(refresh.access_token), "refresh": str(refresh)}, status=200
        )


# ---- Registration + Profiles ----
class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class ProfileViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Profile.objects.select_related("user").all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    @action(detail=False, methods=["get", "patch"])  # /api/profiles/me/
    def me(self, request):
        profile = request.user.profile
        if request.method == "GET":
            return Response(ProfileSerializer(profile).data)
        s = ProfileUpdateSerializer(instance=profile, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response(ProfileSerializer(profile).data)


class CredentialsView(generics.GenericAPIView):
    serializer_class = CredentialsUpdateSerializer

    def patch(self, request):
        s = self.get_serializer(
            data=request.data, partial=True, context={"request": request}
        )
        s.is_valid(raise_exception=True)
        s.update(request.user, s.validated_data)
        return Response({"detail": "Credentials updated."})
