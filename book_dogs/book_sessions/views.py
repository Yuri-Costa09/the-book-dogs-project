from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from .models import BookSession, ReadingSession
from .serializers import BookSessionSerializer, ReadingSessionSerializer
from .services import BookSessionService, ReadingSessionService
from shared.permissions.is_owner import IsOwner


class BookSessionViewSet(viewsets.ModelViewSet):
    serializer_class = BookSessionSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return BookSession.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        try:
            book_session = BookSessionService.create_book_session(
                owner=self.request.user, **serializer.validated_data
            )
            # Update serializer instance to return the created object
            serializer.instance = book_session
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        try:
            book_session = BookSessionService.update_book_session(
                book_session=serializer.instance, **serializer.validated_data
            )
            serializer.instance = book_session
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_destroy(self, instance):
        BookSessionService.delete_book_session(instance)

    @action(detail=True, methods=["get"])
    def statistics(self, request, pk=None):
        book_session = self.get_object()
        stats = BookSessionService.get_reading_statistics(book_session)
        return Response(stats)

    @action(detail=True, methods=["post"])
    def start_reading(self, request, pk=None):
        """Start a new reading session"""
        book_session = self.get_object()
        try:
            reading_session = ReadingSessionService.start_session(
                book_session=book_session, **request.data
            )
            serializer = ReadingSessionSerializer(reading_session)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ReadingSessionViewSet(viewsets.ModelViewSet):
    serializer_class = ReadingSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ReadingSession.objects.filter(
            book_session__owner=self.request.user
        ).select_related("book_session")

    def perform_create(self, serializer):
        book_session_id = serializer.validated_data.get("book_session").id
        book_session = get_object_or_404(
            BookSession, id=book_session_id, owner=self.request.user
        )

        try:
            reading_session = ReadingSessionService.start_session(
                book_session=book_session,
                **{
                    k: v
                    for k, v in serializer.validated_data.items()
                    if k != "book_session"
                }
            )
            serializer.instance = reading_session
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        """Update reading session using service layer"""
        try:
            reading_session = ReadingSessionService.update_session(
                reading_session=serializer.instance, **serializer.validated_data
            )
            serializer.instance = reading_session
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_destroy(self, instance):
        """Delete reading session using service layer"""
        ReadingSessionService.delete_session(instance)

    @action(detail=True, methods=["post"])
    def end_session(self, request, pk=None):
        """End a reading session"""
        reading_session = self.get_object()
        try:
            updated_session = ReadingSessionService.end_session(
                reading_session=reading_session,
                pages_read=request.data.get("pages_read"),
                notes=request.data.get("notes"),
            )
            serializer = self.get_serializer(updated_session)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def statistics(self, request, pk=None):
        """Get session statistics"""
        reading_session = self.get_object()
        stats = ReadingSessionService.get_session_stats(reading_session)
        return Response(stats)
