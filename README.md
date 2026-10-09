# CodeAlpha_EventRegistration

Event Registration System backend — **Django + Django REST Framework + SQLite**.
CodeAlpha Backend Development Internship, Task 2.

## Features
- Models: `Event`, `Registration` (linked to Django `User`)
- Token authentication (signup / login)
- Public event list & details, with live `spots_left`
- Authenticated users can register, view and cancel their registrations
- Capacity check, duplicate-registration prevention, re-register after cancelling
- Organizer features (optional task): Django admin panel + staff-only event create/edit/delete + attendee list

## Setup
```bash
git clone https://github.com/shanmukhanuroop444-del/CodeAlpha_EventRegistration.git
cd CodeAlpha_EventRegistration
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser                   # organizer/admin account
python manage.py runserver
```
Admin panel: http://127.0.0.1:8000/admin/

## API
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/signup/` | – | Create user, returns token |
| POST | `/api/auth/login/` | – | Returns token |
| GET | `/api/events/` | – | List events |
| GET | `/api/events/<id>/` | – | Event details |
| POST | `/api/events/` | Staff | Create event |
| PUT/DELETE | `/api/events/<id>/` | Staff | Edit / delete event |
| POST | `/api/events/<id>/register/` | User | Register for event |
| GET | `/api/registrations/` | User | My registrations |
| DELETE | `/api/registrations/<id>/` | User | Cancel my registration |
| GET | `/api/events/<id>/attendees/` | Staff | Attendee list |

Send the token as header: `Authorization: Token <your-token>`

### Example
```bash
curl -X POST localhost:8000/api/auth/signup/ -d "username=anu&password=secret12"
curl -X POST localhost:8000/api/events/1/register/ -H "Authorization: Token <token>"
```

## Tests
```bash
python manage.py test
```
