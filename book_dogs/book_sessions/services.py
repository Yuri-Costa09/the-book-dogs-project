from datetime import timedelta
from django.db.models import Sum
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import BookSession, ReadingSession


class BookSessionService:
    @staticmethod
    def create_book_session(owner, **data):
        with transaction.atomic():
            # Business rule: validate page number
            if data.get("page_number", 0) <= 0:
                raise ValidationError("Page number must be positive")

            book_session = BookSession.objects.create(owner=owner, **data)
            return book_session

    @staticmethod
    def update_book_session(book_session, **data):
        with transaction.atomic():
            # Business rule: can't reduce page count below current progress
            if "page_number" in data:
                total_pages_read = BookSessionService._get_total_pages_read(
                    book_session
                )
                if data["page_number"] < total_pages_read:
                    raise ValidationError(
                        f"Cannot set page count below current progress ({total_pages_read} pages)"
                    )

            # Auto-mark as finished if progress reaches 100%
            for field, value in data.items():
                setattr(book_session, field, value)

            if BookSessionService.calculate_progress(book_session) >= 100:
                book_session.is_finished = True

            book_session.save()
            return book_session

    @staticmethod
    def delete_book_session(book_session):
        with transaction.atomic():
            # Business logic: stop any active reading sessions
            active_sessions = book_session.reading_sessions.filter(
                end_time__isnull=True
            )
            for session in active_sessions:
                ReadingSessionService.end_session(session)

            book_session.delete()

    @staticmethod
    def calculate_progress(book_session):
        if book_session.page_number <= 0:
            return 0

        total_pages_read = BookSessionService._get_total_pages_read(book_session)
        progress = min((total_pages_read / book_session.page_number) * 100, 100)
        return int(progress)

    @staticmethod
    def get_total_reading_time(book_session):
        sessions = book_session.reading_sessions.filter(end_time__isnull=False)
        total_duration = timedelta(0)
        for session in sessions:
            total_duration += ReadingSessionService.calculate_duration(session)
        return total_duration

    @staticmethod
    def get_reading_statistics(book_session):
        return {
            "progress": BookSessionService.calculate_progress(book_session),
            "total_reading_time": BookSessionService.get_total_reading_time(
                book_session
            ),
            "sessions_count": book_session.reading_sessions.count(),
            "average_session_length": BookSessionService._get_average_session_length(
                book_session
            ),
            "pages_per_session": BookSessionService._get_average_pages_per_session(
                book_session
            ),
        }

    @staticmethod
    def _get_total_pages_read(book_session):
        return (
            book_session.reading_sessions.aggregate(total=Sum("pages_read"))["total"]
            or 0
        )

    @staticmethod
    def _get_average_session_length(book_session):
        sessions = book_session.reading_sessions.filter(end_time__isnull=False)
        if not sessions.exists():
            return timedelta(0)

        total_time = sum(
            [ReadingSessionService.calculate_duration(session) for session in sessions],
            timedelta(0),
        )

        return total_time / sessions.count()

    @staticmethod
    def _get_average_pages_per_session(book_session):
        total_pages = BookSessionService._get_total_pages_read(book_session)
        session_count = book_session.reading_sessions.count()
        return total_pages / session_count if session_count > 0 else 0


class ReadingSessionService:
    @staticmethod
    def start_session(book_session, **data):
        with transaction.atomic():
            # Business rule: only one active session per book
            active_session = book_session.reading_sessions.filter(
                end_time__isnull=True
            ).first()

            if active_session:
                raise ValidationError(
                    "There's already an active reading session for this book"
                )

            # Business rule: can't start session for finished book
            if book_session.is_finished:
                raise ValidationError("Cannot start session for a finished book")

            reading_session = ReadingSession.objects.create(
                book_session=book_session, **data
            )
            return reading_session

    @staticmethod
    def end_session(reading_session, pages_read=None, notes=None):
        with transaction.atomic():
            if reading_session.end_time:
                raise ValidationError("Session is already ended")

            reading_session.end_time = timezone.now()

            if pages_read is not None:
                reading_session.pages_read = pages_read

            if notes is not None:
                reading_session.notes = notes

            reading_session.save()

            # Auto-update book session completion status
            progress = BookSessionService.calculate_progress(
                reading_session.book_session
            )
            if progress >= 100:
                reading_session.book_session.is_finished = True
                reading_session.book_session.save()

            return reading_session

    @staticmethod
    def update_session(reading_session, **data):
        with transaction.atomic():
            # Business rule: can't update ended session's core data
            if reading_session.end_time and "pages_read" in data:
                raise ValidationError("Cannot modify pages read for ended session")

            for field, value in data.items():
                setattr(reading_session, field, value)

            reading_session.save()
            return reading_session

    @staticmethod
    def delete_session(reading_session):
        """Delete reading session with cleanup"""
        with transaction.atomic():
            # Business logic: recalculate book progress after deletion
            book_session = reading_session.book_session
            reading_session.delete()

            # Update book completion status
            progress = BookSessionService.calculate_progress(book_session)
            if progress < 100 and book_session.is_finished:
                book_session.is_finished = False
                book_session.save()

    @staticmethod
    def calculate_duration(reading_session):
        if reading_session.end_time and reading_session.start_time:
            return reading_session.end_time - reading_session.start_time
        return timedelta(0)

    @staticmethod
    def get_session_stats(reading_session):
        duration = ReadingSessionService.calculate_duration(reading_session)
        pages_per_minute = 0

        if duration.total_seconds() > 0 and reading_session.pages_read:
            pages_per_minute = reading_session.pages_read / (
                duration.total_seconds() / 60
            )

        return {
            "duration": duration,
            "pages_read": reading_session.pages_read,
            "pages_per_minute": round(pages_per_minute, 2),
            "is_active": reading_session.end_time is None,
        }
