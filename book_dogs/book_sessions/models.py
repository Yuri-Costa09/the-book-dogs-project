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

    @property
    def progress(self):
        """Calculate progress as percentage of pages read from all reading sessions"""
        if self.page_number <= 0:
            return 0

        total_pages_read = sum(
            session.pages_read or 0 for session in self.reading_sessions.all()
        )

        progress_percentage = min((total_pages_read / self.page_number) * 100, 100)
        return int(progress_percentage)


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

    @property
    def duration(self):
        """Calculate duration as end_time - start_time"""
        if self.end_time and self.start_time:
            return self.end_time - self.start_time
        return None
