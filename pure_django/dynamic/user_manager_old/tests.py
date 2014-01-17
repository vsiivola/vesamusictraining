from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse

class SimpleTest(TestCase):
  client=Client()
  
  #def setUp(self):
  #    self.u1 = User.objects.create(username='user1')
  
  #def tearDown(self):
  #    self.u1.delete()
  
  def test_pages_exist(self):
    res = self.client.get(reverse('user_manager.views.register'))
    res = self.client.get(reverse('user_manager.views.logout_view'))
                            
