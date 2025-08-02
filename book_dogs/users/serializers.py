from rest_framework import serializers
from .models import User, Profile


class UserRegistrationSerializer(serializers.ModelSerializer):
    # Make password write-only & required, so it doesn't return in the response
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]
        extra_kwargs = {
            "email": {"required": True},  # Make email required
            "username": {"required": True},  # Make username required
        }

    # Use django auth implementation to create user with hashed password
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "username", "email"]


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"
        extra_kwargs = {
            "user": {"required": True},
            "bio": {"required": False},
            "city": {"required": False},
            "profile_picture": {"required": False},
            "website": {"required": False},
        }
