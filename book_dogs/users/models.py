from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    email = models.EmailField(unique=True)

    @property
    def total_books(self):
        """Get total number of book sessions for this user"""
        return self.book_sessions.count()

    @property
    def finished_books(self):
        """Get finished book sessions for this user"""
        return self.book_sessions.filter(status="finished").count()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    city = models.CharField(max_length=255, blank=True)
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
