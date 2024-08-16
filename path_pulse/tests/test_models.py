from django.test import TestCase
from ..models import User, Trip

test_email = 'test_user@email.com'
test_city = 'Los Angeles'
test_state = 'California'
test_country = 'US'
test_start_date = '2024-08-26'
test_end_date = '2024-08-30'

class UserTestCase(TestCase):
    def setUp(self):
        User.objects.create(user_email= test_email)

    def test_user_get(self):
        user = User.objects.get(user_email= test_email)
        self.assertEqual(str(user), test_email)


class TripTestCase(TestCase):
    def  setUp(self):
        user = User.objects.create(user_email=test_email)
        Trip.objects.create(
            user= user,
            city= test_city,
            state= test_state,
            country= test_country,
            start_date= test_start_date,
            end_date= test_end_date,
        )

    def test_trip_get(self):
        user = User.objects.get(user_email= test_email)
        trip = Trip.objects.get(user = user)
        trip_string = str(trip)
        self.assertTrue(trip)
        self.assertIn(test_city, trip_string)
        self.assertIn(test_state, trip_string)
        self.assertIn(test_country, trip_string)
        self.assertIn(test_start_date, trip_string)
        self.assertIn(test_end_date, trip_string)