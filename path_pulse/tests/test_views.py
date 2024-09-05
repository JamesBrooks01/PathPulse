from django.test import TestCase
from django.urls import reverse
import datetime
from datetime import date

from ..models import Trip, User

test_email = 'test_user@email.com'
test_city = 'Los Angeles'
test_state = 'California'
test_country = 'US'
test_start_date = '2024-08-26'
test_end_date = '2024-08-30'

class IndexGuestViewTests(TestCase):
    def test_guest_visit(self):
        response = self.client.get(reverse('path_pulse:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You are currently logged in as a guest.')

class IndexInitialUserTests(TestCase):
    def  setUp(self):
        session = self.client.session
        session['user'] = {"userinfo": {"email": test_email,"name": "TestUser","picture": "https://cdn.pixabay.com/photo/2017/11/10/05/46/group-2935521_1280.png"}}
        session.save()

    def test_index_create_db_user(self):
        redirect_response = self.client.get(reverse('path_pulse:index'))
        self.assertRedirects(redirect_response, reverse('path_pulse:index'))
        response_attempt2 = self.client.get(reverse('path_pulse:index'))
        self.assertEqual(response_attempt2.status_code, 200)
        self.assertContains(response_attempt2, 'Trip Location')

class IndexViewTest(TestCase):
    def  setUp(self):
        session = self.client.session
        session['user'] = {'userinfo': {"email": test_email, 'name': 'TestUser', 'picture': 'https://cdn.pixabay.com/photo/2017/11/10/05/46/group-2935521_1280.png'}}
        session.save()
        User.objects.create(user_email=test_email)

    def test_no_trips(self):
        response = self.client.get(reverse('path_pulse:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Trip Location')

    def test_1_trip(self):
        user = User.objects.get(user_email= test_email)
        Trip.objects.create(
            user= user,
            city= test_city,
            state= test_state,
            country= test_country,
            start_date= test_start_date,
            end_date= test_end_date,
        )
        response = self.client.get(reverse('path_pulse:index'))
        self.assertContains(response, 'Location:')
        self.assertContains(response, 'Start Date:')
        self.assertContains(response, 'End Date:')

class VoteViewNoUserTest(TestCase):
    def test_no_user_redirect(self):
        redirect_response = self.client.get(reverse('path_pulse:vote', kwargs={'user_id': 0}))
        self.assertRedirects(redirect_response,  reverse('path_pulse:index'))

class VoteViewUserDoesNotExistTest(TestCase):
    def  setUp(self):
        session = self.client.session
        session['user'] = {'userinfo': {"email": test_email, 'name': 'TestUser', 'picture': 'https://cdn.pixabay.com/photo/2017/11/10/05/46/group-2935521_1280.png'}}
        session.save()

    def test_user_logged_but_not_in_database(self):
        response = self.client.get(reverse('path_pulse:vote', kwargs={'user_id': 0}))
        self.assertContains(response, "User does not exist in the database")

class VoteViewTests(TestCase):
    def  setUp(self):
        session = self.client.session
        session['user'] = {'userinfo': {"email": test_email, 'name': 'TestUser', 'picture': 'https://cdn.pixabay.com/photo/2017/11/10/05/46/group-2935521_1280.png'}}
        session.save()
        User.objects.create(user_email=test_email)

    def test_userid_not_same_as_db_userid(self):
        response = self.client.get(reverse('path_pulse:vote', kwargs={'user_id': 0}))
        self.assertContains(response, "The currently logged in user")

    def test_intended_path(self):
        user = User.objects.get(user_email= test_email)
        path = reverse('path_pulse:vote', kwargs={'user_id': user.id})
        data = {'city': test_city, 'state': test_state, 'country': test_country, 'start_date': test_start_date, 'end_date': test_end_date}
        response = self.client.post(path=path, data=data)
        self.assertRedirects(response, reverse('path_pulse:index'))

    def test_incomplete_form(self):
        user = User.objects.get(user_email= test_email)
        path = reverse('path_pulse:vote', kwargs={'user_id': user.id})
        data = {'city': test_city, 'state': test_state, 'country': test_country, 'start_date': test_start_date}
        response = self.client.post(path=path, data=data)
        self.assertContains(response, "An Error has occurred")

class DeleteTripTestNoUser(TestCase):
    def test_no_logged_in_user(self):
        path = reverse('path_pulse:delete_trip', kwargs={'trip_id': 1})
        response = self.client.get(path=path)
        self.assertRedirects(response, reverse('path_pulse:index'))

class DeleteTripTest(TestCase):
    def  setUp(self):
        session = self.client.session
        session['user'] = {'userinfo': {"email": test_email, 'name': 'TestUser', 'picture': 'https://cdn.pixabay.com/photo/2017/11/10/05/46/group-2935521_1280.png'}}
        session.save()
        User.objects.create(user_email=test_email)
        user = User.objects.get(user_email= test_email)
        path = reverse('path_pulse:vote', kwargs={'user_id': user.id})
        data = {'city': test_city, 'state': test_state, 'country': test_country, 'start_date': test_start_date, 'end_date': test_end_date}
        self.client.post(path=path, data=data)

    def test_intended_path(self):
        user = User.objects.get(user_email= test_email)
        trip = Trip.objects.get(user=user)
        path = reverse('path_pulse:delete_trip', kwargs={'trip_id': trip.id})
        response = self.client.get(path=path)
        self.assertRedirects(response, reverse('path_pulse:index'))

    def test_trip_does_not_exist(self):
        user = User.objects.get(user_email= test_email)
        trip = Trip.objects.get(user=user)
        adjusted_trip_id = trip.id + 1
        path = reverse('path_pulse:delete_trip', kwargs={'trip_id': adjusted_trip_id})
        response = self.client.get(path=path)
        self.assertContains(response, "Either the Trip or User does not Exist")
    
    def test_trip_and_user_different_ids(self):
        User.objects.create(user_email="user2@email.com")
        user = User.objects.get(user_email= "user2@email.com")
        Trip.objects.create(
            user= user,
            city= test_city,
            state= test_state,
            country= test_country,
            start_date= test_start_date,
            end_date= test_end_date,
        )

        trip = Trip.objects.get(user=user)
        delete_path = reverse('path_pulse:delete_trip', kwargs={'trip_id': trip.id})
        response = self.client.get(path=delete_path)
        self.assertContains(response, "action is unauthorized")

class TripPrintNoUserTest(TestCase):
    def test_no_logged_in_user(self):
        path = reverse('path_pulse:print_test', kwargs={'trip_id': 1})
        response = self.client.get(path=path)
        self.assertRedirects(response, reverse('path_pulse:index'))

class TripPrintTest(TestCase):
    def  setUp(self):
        session = self.client.session
        session['user'] = {'userinfo': {"email": test_email, 'name': 'TestUser', 'picture': 'https://cdn.pixabay.com/photo/2017/11/10/05/46/group-2935521_1280.png'}}
        session.save()
        User.objects.create(user_email=test_email)
        user = User.objects.get(user_email= test_email)
        path = reverse('path_pulse:vote', kwargs={'user_id': user.id})
        today = date.today()
        start_object  = today + datetime.timedelta(14)
        end_object = today + datetime.timedelta(20)
        data = {'city': test_city, 'state': test_state, 'country': test_country, 'start_date': start_object.isoformat(), 'end_date': end_object.isoformat()}
        self.client.post(path=path, data=data)

    def test_intended_path(self):
        user = User.objects.get(user_email= test_email)
        trip = Trip.objects.get(user=user)
        path = reverse('path_pulse:print_test', kwargs={'trip_id': trip.id})
        response = self.client.get(path=path)
        self.assertContains(response, "The Weather should be")

    def test_trip_does_not_exist(self):
        user = User.objects.get(user_email= test_email)
        trip = Trip.objects.get(user=user)
        adjusted_trip_id = trip.id + 1
        path = reverse('path_pulse:print_test', kwargs={'trip_id': adjusted_trip_id})
        response = self.client.get(path=path)
        self.assertContains(response, "trip does not Exist")
    
    def test_trip_and_user_different_ids(self):
        User.objects.create(user_email="user2@email.com")
        user = User.objects.get(user_email= "user2@email.com")
        Trip.objects.create(
            user= user,
            city= test_city,
            state= test_state,
            country= test_country,
            start_date= test_start_date,
            end_date= test_end_date,
        )

        trip = Trip.objects.get(user=user)
        delete_path = reverse('path_pulse:print_test', kwargs={'trip_id': trip.id})
        response = self.client.get(path=delete_path)
        self.assertContains(response, "match with the user assosiated")