"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from app.models import *

"""
To save a fixture using current database:
./manage.py dumpdata app auth --all --indent=2 > app/fixtures/test_fixture.json
"""

"""
List of Tests for Posterboard Handler
# Normal Behavior Test
- Create a new Posterboard with good parameters, 
    verify that it is placed in the User's Posterboard set, then Delete it
- Create a new Posterboard with private = False and check that everyone can access it
- Create a new Posterboard with private = True and 
    check that only the blogger can see it on the blogger's home page

# Bad Behavior Test
- Create a new Posterboard with bad parameters (Invalid Title Length)
- Create two new Posterboard with the same title
- Delete a non-existing Posterboard
- Modify a non-existing PosterBoard
- Create a new Posterbaord without a blogger

# Small Stress Test
- Simultaneously create 10 good Posterboard 
- Simultaneously create 10 bad Posterboard with same title
"""
        
"""
List of Tests for Element Handler
# Normal Behavior Test
- Create and store an image object with good parameters,
    verify that it is placed in the Posterboard's Element set, then Delete it
- Update an element (by "saving")

# Bad Behavior Test
- Create an element object with invalid type
- Create an element with type='image' but do not provide correct image parameter
- Create an state with bad position     (out of range)
- Create an state with bad orientation  (out of range)
- Create an state with bad opacity      (out of range)
- Create an state with bad delay time   (out of range)
- Create an state with bad speed        (out of range)

# Small Stress Test
- Create 10 Element on a Posterboard
- Update 10 Element on a Posterboard
"""

"""
List of Tests for Profile Handler
# Normal Behavior Test
- Get basic personal information from profile page
- Change personal information and get basic personal information again to
    verify that it correctly display the updated information

# Bad Behavior Test
- If a user tries to Get basic personal information when not logged in
    should receive a redirect to the login page
"""
class ProfileHandlerTest(TestCase):
    fixtures = ['test_fixture.json']
    
    def setUp(self):        
        username = 'test'
        password = 'test'
        self.user = User.objects.get(username=username)
        
        self.c = Client()
        self.c.login(username=username, password=password)
        
    def test_get_profile(self):
        response = self.c.get('/profile/.json')
        container = eval(response._container[0])
        profile = container['profile']
        self.assertEqual(profile['username'],self.user.username)
        self.assertEqual(profile['email'],self.user.email) 
        
    def test_change_get_profile(self):
        new_email = 'new_'+self.user.email
        self.user.email = new_email
        self.user.save()
        self.test_get_profile()
    
    def test_not_logged_in(self):
        self.c.logout()
        response = self.c.get('/profile/.json')
        self.assertEqual(response.status_code,302)