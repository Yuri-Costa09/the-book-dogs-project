from django.urls import path
from .views import UserRegisterView, CreateProfileView, ProfileDetailView

urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="register"),
    path("profile/", CreateProfileView.as_view(), name="profile"),
    path("profile/<int:pk>/", ProfileDetailView.as_view(), name="profile-detail"),
]
