"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from app.models import *
from app.forms import *
import os

"""
To save a fixture using current database:
./manage.py dumpdata app auth --all --indent=2 > app/fixtures/test_fixture.json
"""

"""
Helper method to simulate a client login as User with username and password
Returns [client, user]
"""
def login_user (username, password):
    user = User.objects.get(username=username)
    c = Client()
    c.login(username=username, password=password)
    return [c, user]

"""
List of Tests for Posterboard Handler
# Normal Behavior Test
- Create a new Posterboard with good parameters, 
    verify that it is placed in the User's Posterboard set, then Delete it
- Create a new Posterboard with private = False and check that everyone can access it
- Create a new Posterboard with private = True and 
    check that only the blogger can see it on the blogger's home page

# Bad Behavior Test
- Create a new Posterboard with bad parameter (Invalid Title Length)
- Create a new Posterboard with bad parameter (Invalid private field)
- Create two new Posterboard with the same title
- Delete a non-existing Posterboard
- Modify a non-existing PosterBoard
- Create a new Posterbaord without a blogger

# Small Stress Test
- Simultaneously create 10 good Posterboard 
- Simultaneously create 10 bad Posterboard with same title
"""

class PosterboardHandlerTest (TestCase):
    fixtures = ['test_fixture.json']
    
    def setUp(self):        
        [self.c, self.user] = login_user('test','test')
        self.homepath = '/people/'+self.user.username+'/posterboards/'
             
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
class ElementHandlerTest (TestCase):
    fixtures = ['test_fixture.json']
    
    def setUp(self):
        [self.c, self.user] = login_user('test','test')
        self.pb = Posterboard.objects.filter(user__username=self.user.username)[0]
        self.pbpath = '/people/'+self.user.username+'/posterboards/'+self.pb.title_path+'/elements/'

        # Create a temporary image for testing
        self.imagepath = 'test.png'
        self.image = open(self.imagepath,'w')
        self.image.close()
    
    def create_image(self):
        img = open(self.imagepath,'rb')
        data = {
            'element-type':'image',
            'image':img
        }
        response = self.c.post(self.pbpath+'.json',data)
        img.close()
        return response
    
    def delete_element(self, id):
        response = self.c.delete(self.pbpath+str(id)+'/.json')
        return response
    
    def test_create_good_image(self):
        response = self.create_image()
        container = eval(response._container[0])
        self.assertEqual(response.status_code, 200)
        element_id = container['element_id']
        self.assertEqual(self.pb.title,Element.objects.get(pk=element_id).posterboard.title)
        self.assertEqual(self.delete_element(element_id).status_code, 200)
        self.assertEqual(len(Element.objects.filter(pk=element_id)), 0)

    def test_create_invalid_type(self):
        data = {
            'element-type':'invalid-type',
        }
        response = self.c.post(self.pbpath+'.json',data)
        self.assertEqual(response.status_code, 400)
    
    def test_create_good_type_invalid_parameter(self):
        data = {
            'element-type':'image',
            'image':'Not_a_path'
        }
        response = self.c.post(self.pbpath+'.json',data)
        self.assertEqual(response.status_code, 400)

    def tearDown(self):
        os.remove(self.imagepath)

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
        [self.c, self.user] = login_user('test','test')      
       
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