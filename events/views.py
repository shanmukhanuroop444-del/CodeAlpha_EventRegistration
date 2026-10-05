from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Event, Registration
from .serializers import EventSerializer, RegistrationSerializer, SignupSerializer


class IsStaffOrReadOnly(permissions.BasePermission):
    """Anyone can read; only staff (event organizers) can create/edit/delete."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class SignupView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        ser = SignupSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"username": user.username, "token": token.key}, status=status.HTTP_201_CREATED)


class EventListCreate(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsStaffOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)


class EventDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsStaffOrReadOnly]


class RegisterForEvent(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, pk):
        event = get_object_or_404(Event.objects.select_for_update(), pk=pk)
        reg = Registration.objects.filter(user=request.user, event=event).first()

        if reg and reg.status == Registration.ACTIVE:
            return Response({"error": "You are already registered for this event."}, status=400)
        if event.spots_left <= 0:
            return Response({"error": "This event is full."}, status=400)

        if reg:  # re-register after cancelling
            reg.status = Registration.ACTIVE
            reg.save()
        else:
            reg = Registration.objects.create(user=request.user, event=event)
        return Response(RegistrationSerializer(reg).data, status=status.HTTP_201_CREATED)


class MyRegistrations(generics.ListAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Registration.objects.filter(user=self.request.user).select_related("event")


class CancelRegistration(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        reg = get_object_or_404(Registration, pk=pk, user=request.user)
        reg.status = Registration.CANCELLED
        reg.save()
        return Response({"message": "Registration cancelled."})


class EventAttendees(generics.ListAPIView):
    """Organizer view: who registered for an event."""
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Registration.objects.filter(event_id=self.kwargs["pk"], status=Registration.ACTIVE)
