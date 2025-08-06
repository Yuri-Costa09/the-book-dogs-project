from django.urls import path
from .views import (
    UserRegisterView,
    CreateProfileView,
    ProfileDetailView,
    UpdateProfileView,
    DeleteProfileView,
)

urlpatterns = [
    path("register/", UserRegisterView.as_view(), name="register"),
    path("profile/", CreateProfileView.as_view(), name="profile"),
    path("profile/<int:pk>/", ProfileDetailView.as_view(), name="profile-detail"),
    path(
        "profile/<int:pk>/update/", UpdateProfileView.as_view(), name="profile-update"
    ),
    path(
        "profile/<int:pk>/delete/", DeleteProfileView.as_view(), name="profile-delete"
    ),
]
