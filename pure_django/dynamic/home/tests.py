import sys

from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

class SimpleTest(TestCase):
    client = Client()

    def test_homepage_exists(self):
        res = self.client.get(reverse('home.views.home'))

    def test_auth_redirect(self):
        self.u1 = User.objects.create_user("testuser1", 'testmail1@nothing', password="testpass1")
        client_auth=Client()
        response = client_auth.post('/accounts/login/', {'username': 'testuser1', 'password': 'testpass1'})
        sys.stderr.write(repr(response))
        #self.assertRedirects(response, '/exercise/') # Why does this want to find a 404 page?

