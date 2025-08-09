from rest_framework import serializers
from .models import BookSession, ReadingSession
from .services import BookSessionService, ReadingSessionService


class BookSessionSerializer(serializers.ModelSerializer):
    progress = serializers.SerializerMethodField()
    total_reading_time = serializers.SerializerMethodField()

    class Meta:
        model = BookSession
        fields = [
            "id",
            "owner",
            "progress",
            "total_reading_time",
            "title",
            "description",
            "page_number",
            "is_finished",
            "author",
            "genre",
            "cover_image",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["owner", "progress", "total_reading_time"]

    def get_progress(self, obj):
        """Get progress using service layer"""
        return BookSessionService.calculate_progress(obj)

    def get_total_reading_time(self, obj):
        """Get total reading time as seconds"""
        total_time = BookSessionService.get_total_reading_time(obj)
        return int(total_time.total_seconds())


class ReadingSessionSerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField()

    class Meta:
        model = ReadingSession
        fields = [
            "id",
            "book_session",
            "pages_read",
            "start_time",
            "end_time",
            "duration",
            "notes",
            "is_finished",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["duration"]

    def get_duration(self, obj):
        """Get duration as seconds using service layer"""
        duration = ReadingSessionService.calculate_duration(obj)
        return int(duration.total_seconds())
