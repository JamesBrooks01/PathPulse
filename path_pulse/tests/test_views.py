from django.test import TestCase
from django.urls import reverse

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

