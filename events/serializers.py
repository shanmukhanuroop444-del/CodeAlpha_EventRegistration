from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Event, Registration


class EventSerializer(serializers.ModelSerializer):
    spots_left = serializers.IntegerField(read_only=True)
    organizer = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Event
        fields = ["id", "title", "description", "location", "date", "capacity", "spots_left", "organizer"]


class RegistrationSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Registration
        fields = ["id", "user", "event", "status", "created_at"]


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated):
        return User.objects.create_user(**validated)
