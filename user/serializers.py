from rest_framework import serializers
from .models import User
from django.contrib.auth.hashers import make_password

class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password", "username", "display_name", "user_type", "phone_number"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        email = data.get("email")
        phone = data.get("phone_number")

        if not email and not phone:
            raise serializers.ValidationError("Email or Phone number is required")

        if email and User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already exists")

        if phone and User.objects.filter(phone_number=phone).exists():
            raise serializers.ValidationError("Phone number already exists")

        return data

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        validated_data["is_verified"] = False
        return User.objects.create(**validated_data)
