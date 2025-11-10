from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("phone_number", "password", "username")
        extra_kwargs = {"password": {"write_only": True, "required": False}}

    def create(self, validated):
        password = validated.pop("password", None)
        user = User.objects.create(**validated)
        if password:
            user.set_password(password)
            user.save()
        return user


class ProfileSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source="user.phone_number", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Profile
        fields = ("phone_number", "username", "full_name", "bio", "avatar_url")


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("full_name", "bio", "avatar_url")


class CredentialsUpdateSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(required=False, write_only=True, min_length=8)

    def validate_username(self, value):
        user_model = self.context["request"].user.__class__
        if (
            value
            and user_model.objects.filter(username=value)
            .exclude(pk=self.context["request"].user.pk)
            .exists()
        ):
            raise serializers.ValidationError("Username already taken.")
        return value

    def update(self, instance, validated):
        if "username" in validated:
            instance.username = validated["username"] or None
        if "password" in validated:
            instance.set_password(validated["password"])
        instance.save()
        return instance


class OTPStartSerializer(serializers.Serializer):
    phone_number = serializers.CharField()


class OTPVerifySerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp = serializers.CharField()
