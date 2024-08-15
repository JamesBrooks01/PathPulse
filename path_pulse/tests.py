from django.test import TestCase
from django.urls import reverse

from .models import Trip, User

test_email = 'test_user@email.com'

class UserTestCase(TestCase):
    def setUp(self):
        User.objects.create(user_email= test_email)

    def test_user_get(self):
        user = User.objects.get(user_email= test_email)
        self.assertEqual(str(user), test_email)


class TripTestCase(TestCase):
    pass
