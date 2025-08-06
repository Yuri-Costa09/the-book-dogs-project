from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.generics import RetrieveAPIView
from .serializers import UserRegistrationSerializer, ProfileSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import User, Profile
from rest_framework.exceptions import PermissionDenied
from shared.permissions.is_owner import IsOwner


# Register endpoint, basically creating an user.
class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    queryset = User.objects.all()


class CreateProfileView(generics.CreateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = Profile.objects.all()


class ProfileDetailView(RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = Profile.objects.all()


class UpdateProfileView(generics.UpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    queryset = Profile.objects.all()

    def get_object(self):
        return self.request.user.profile


class DeleteProfileView(generics.DestroyAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    queryset = Profile.objects.all()

    def get_object(self):
        return self.request.user.profile
