from django.db import models
from users.models import User

# Create your models here.


class BookSession(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="book_sessions"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    page_number = models.IntegerField()
    is_finished = models.BooleanField(default=False)
    author = models.CharField(max_length=255)
    genre = models.CharField(max_length=255)
    cover_image = models.ImageField(upload_to="cover_images/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ReadingSession(models.Model):
    book_session = models.ForeignKey(
        BookSession, on_delete=models.CASCADE, related_name="reading_sessions"
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    pages_read = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    is_finished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
