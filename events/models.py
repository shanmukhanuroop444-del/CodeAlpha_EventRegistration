from django.conf import settings
from django.db import models


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200)
    date = models.DateTimeField()
    capacity = models.PositiveIntegerField(default=50)
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="organized_events"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return self.title

    @property
    def active_registrations(self):
        return self.registrations.filter(status=Registration.ACTIVE).count()

    @property
    def spots_left(self):
        return max(self.capacity - self.active_registrations, 0)


class Registration(models.Model):
    ACTIVE, CANCELLED = "active", "cancelled"
    STATUS_CHOICES = [(ACTIVE, "Active"), (CANCELLED, "Cancelled")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="registrations")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "event")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} -> {self.event} ({self.status})"
