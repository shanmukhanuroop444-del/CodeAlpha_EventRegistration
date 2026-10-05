from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from . import views

urlpatterns = [
    path("auth/signup/", views.SignupView.as_view()),
    path("auth/login/", obtain_auth_token),
    path("events/", views.EventListCreate.as_view()),
    path("events/<int:pk>/", views.EventDetail.as_view()),
    path("events/<int:pk>/register/", views.RegisterForEvent.as_view()),
    path("events/<int:pk>/attendees/", views.EventAttendees.as_view()),
    path("registrations/", views.MyRegistrations.as_view()),
    path("registrations/<int:pk>/", views.CancelRegistration.as_view()),
]
