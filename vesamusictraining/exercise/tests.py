import sys

from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from exercise.models import Log, UserLecture

class SimpleTest(TestCase):
  def setUp(self):
    self.client_auth=Client()
    self.u1 = User.objects.create_user("test_user1", 'testmail1@nothing', password="testpass1")
    #response = self.client_auth.post('/accounts/login/', {'username': 'testuser1', 'password': 'testpass1'})
    self.assertTrue(self.client_auth.login(username="test_user1", password="testpass1"))

  def tearDown(self):
    self.u1.delete()

  def test_auth_ajax(self):
    response = self.client_auth.get(reverse('exercise.views.list_lectures'))
    self.assertEqual(response.status_code, 200)
    response = self.client_auth.get("/exercise/Debug/lecture/", {'exercise_index': 0})
    self.assertEqual(response.status_code, 200)
    response = self.client_auth.get("/exercise/Debug/verify/", {
        'exercise_index': 0, 'chosen_image':'/site_media/generated_assets/images/Simple_tones-1.png'})
    self.assertEqual(response.status_code, 200)
    response = self.client_auth.get('/exercise/Debug/complete/', {'num_correct':1})
    self.assertEqual(response.status_code, 200)

    # Check that the list render works when there are completed lectures
    response = self.client_auth.get(reverse('exercise.views.list_lectures'))
    self.assertEqual(response.status_code, 200)
    
  def test_unauth(self):
    unauth_client = Client()
    response = self.client_auth.get("/exercise/Debug/lecture/", {'exercise_index': 1})
    # FIXME: This is not a correct test
    self.assertEqual(response.status_code, 200)

  def test_log(self):
    log = Log.objects.create(user=self.u1, entry="logtest")
    
  def test_userexercise(self):
    ue = UserLecture(user=self.u1, lecture_name="test_ex1", lecture_version="0.0",
                      num_questions=10, score=5)
    
