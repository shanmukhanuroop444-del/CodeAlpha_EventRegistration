from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APITestCase

from .models import Event


class EventAPITests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user("org", password="pass1234", is_staff=True)
        self.event = Event.objects.create(
            title="Hackathon", location="Hyderabad", date=timezone.now(), capacity=1, organizer=self.admin
        )

    def signup(self, name):
        r = self.client.post("/api/auth/signup/", {"username": name, "password": "secret12"})
        self.assertEqual(r.status_code, 201)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + r.data["token"])

    def test_list_and_detail_public(self):
        self.assertEqual(self.client.get("/api/events/").status_code, 200)
        self.assertEqual(self.client.get(f"/api/events/{self.event.id}/").data["spots_left"], 1)

    def test_register_requires_login(self):
        self.assertEqual(self.client.post(f"/api/events/{self.event.id}/register/").status_code, 401)

    def test_register_duplicate_and_full(self):
        self.signup("a")
        self.assertEqual(self.client.post(f"/api/events/{self.event.id}/register/").status_code, 201)
        self.assertEqual(self.client.post(f"/api/events/{self.event.id}/register/").status_code, 400)
        self.signup("b")
        self.assertEqual(self.client.post(f"/api/events/{self.event.id}/register/").status_code, 400)  # full

    def test_cancel_frees_spot(self):
        self.signup("a")
        reg_id = self.client.post(f"/api/events/{self.event.id}/register/").data["id"]
        self.assertEqual(self.client.delete(f"/api/registrations/{reg_id}/").status_code, 200)
        self.assertEqual(self.client.get(f"/api/events/{self.event.id}/").data["spots_left"], 1)
        self.assertEqual(len(self.client.get("/api/registrations/").data), 1)

    def test_only_staff_create_event(self):
        self.signup("a")
        body = {"title": "X", "location": "Y", "date": "2026-12-01T10:00:00Z", "capacity": 5}
        self.assertEqual(self.client.post("/api/events/", body).status_code, 403)
        self.client.credentials()
        self.client.force_authenticate(self.admin)
        self.assertEqual(self.client.post("/api/events/", body).status_code, 201)

    def test_cannot_cancel_others(self):
        self.signup("a")
        reg_id = self.client.post(f"/api/events/{self.event.id}/register/").data["id"]
        self.signup("b")
        self.assertEqual(self.client.delete(f"/api/registrations/{reg_id}/").status_code, 404)
