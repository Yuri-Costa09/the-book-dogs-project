from rest_framework import serializers
from .models import BookSession, ReadingSession


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookSession
        fields = [
            "id",
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


class ReadingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingSession
        fields = [
            "id",
            "book_session",
            "pages_read",
            "start_time",
            "end_time",
            "created_at",
            "updated_at",
        ]
