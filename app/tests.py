"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from app.decorators import test_concurrently
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
    
    def create_posterboard(self, title, private):
        data = {
            'title': title,
            'private': private
        }
        response = self.c.post(self.homepath[:-1]+'.json',data)
        return response

    def delete_posterboard(self, id):
        response = self.c.delete(self.homepath+str(id)+'/.json')
        return response
    
    def test_create_delete_one_posterboard(self):
        title = 'testPosterBoardPost'
        response = self.create_posterboard(title, False)
        container = eval(response._container[0])
        self.assertEqual(response.status_code, 200)
        pb_id = container['posterboard-id']
        
        self.assertEqual(title,Posterboard.objects.get(pk=pb_id).title)
        self.assertEqual(self.delete_posterboard(pb_id).status_code, 200)
        self.assertEqual(len(Posterboard.objects.filter(pk=pb_id)), 0)
    
             
"""
List of Tests for Element Handler
# Normal Behavior Test
- Create and store an image object with good parameters,
    verify that it is placed in the Posterboard's Element set, then Delete it
- Create an image object, update the alt text, and verify that the change took place

# Bad Behavior Test
- Create an element object with invalid type
- Create an element with type='image' but do not provide correct image parameter

# Good and Bad Behavior Test
- Create an state with orientation
- Create an state with opacity
- Create an state with delay time
- Create an state with speed

# Small Stress Test
- Simultaneously Create 15 Element on a Posterboard
- Simultaneously Update 15 Element on a Posterboard
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
        response = self.c.post(self.pbpath[:-1]+'.json',data)
        img.close()
        return response
    
    def delete_element(self, id):
        data = {
            '_action':'delete'
        }
        response = self.c.get(self.pbpath+str(id)+'/.json',data)
        return response
    
    def test_create_delete_one_image(self):
        response = self.create_image()
        container = eval(response._container[0])
        self.assertEqual(response.status_code, 200)
        element_id = container['element-id']
        self.assertEqual(self.pb.title,Element.objects.get(pk=element_id).posterboard.title)
        self.assertEqual(self.delete_element(element_id).status_code, 200)
        self.assertEqual(len(Element.objects.filter(pk=element_id)), 0)

    def update_image_wrapper(self, state_id, xPos, yPos, alt):
        state = State.objects.get(pk=state_id)
        image = ImageState.objects.get(pk=state_id)
        beforeUpdateURL = image.image.url
        
        data = {
            '_action':'put',
            'element-type':'image',
            'state-id': state_id,
            'state-position_x': xPos,
            'state-position_y': yPos,
            'child-id': state_id,
            'image-alt': alt
        }
        response = self.c.post(self.pbpath[:-1]+'.json',data)
        
        state = State.objects.get(pk=state_id)
        image = ImageState.objects.get(pk=state_id)
        self.assertEqual(beforeUpdateURL,image.image.url)
        self.assertEqual(alt,image.alt)
        self.assertEqual(xPos,state.position_x)
        self.assertEqual(yPos,state.position_y)
    
    def test_update_one_image(self):
        response = self.create_image()
        container = eval(response._container[0])
        self.assertEqual(response.status_code, 200)
        element_id = container['element-id']
        state_id = container['state-id']
        self.assertEqual(self.pb.title,Element.objects.get(pk=element_id).posterboard.title)
        
        self.update_image_wrapper(state_id,50,0,'test alt')
        
        self.assertEqual(self.delete_element(element_id).status_code, 200)
        self.assertEqual(len(Element.objects.filter(pk=element_id)), 0) 
    
    def test_stress_simultaneous_same_user_create_delete(self, n=15):
        @test_concurrently(n)
        def concurrent_create_delete():
            self.test_create_delete_one_image()
        numStates = ImageState.objects.count()
        concurrent_create_delete()
        self.assertEqual(ImageState.objects.count(), numStates)

    def test_stress_simultaneous_same_user_create_update_delete(self, n=15):
        @test_concurrently(n)
        def concurrent_create_delete():
            self.test_update_one_image
        numStates = ImageState.objects.count()
        concurrent_create_delete()
        self.assertEqual(ImageState.objects.count(), numStates)
    
    def test_create_element_invalid_type(self):
        data = {
            'element-type':'invalid-type',
        }
        response = self.c.post(self.pbpath[:-1]+'.json',data)
        self.assertEqual(response.status_code, 400)
    
    def test_create_element_good_type_invalid_parameter(self):
        data = {
            'element-type':'image',
            'image':'Not_a_path'
        }
        response = self.c.post(self.pbpath[:-1]+'.json',data)
        self.assertEqual(response.status_code, 400)

    def create_state(self, x_pos = None, y_pos = None, orientation = None,
                            opacity = None, delay = None, speed = None):
        img = open(self.imagepath,'rb')
        data = {
            'element-type':'image',
            'image':img
        }
        
        if not x_pos == None:
            data['state-position_x'] = x_pos
        if not y_pos == None:
            data['state-position_y'] = y_pos
        if not orientation == None:
            data['state-orientation'] = orientation
        if not opacity == None:
            data['state-opacity'] = opacity
        if not delay == None:
            data['state-delay'] = delay
        if not speed == None:
            data['state-speed'] = speed

        response = self.c.post(self.pbpath[:-1]+'.json',data)
        img.close()
        return response

    def test_create_state_good_bad_orientation(self):
        response = self.create_state(orientation=180)
        self.assertEqual(response.status_code, 200)
        response = self.create_state(orientation=360)
        self.assertEqual(response.status_code, 400)
    
    def test_create_state_good_bad_opacity(self):
        response = self.create_state(opacity=0.5)
        self.assertEqual(response.status_code, 200)
        response = self.create_state(opacity=2.0)
        self.assertEqual(response.status_code, 400)

    def test_create_state_good_bad_delay_time(self):
        response = self.create_state(delay=1.0)
        self.assertEqual(response.status_code, 200)
        response = self.create_state(delay=-1.0)
        self.assertEqual(response.status_code, 400)

    def test_create_state_good_bad_speed(self):    
        response = self.create_state(speed=5000)
        self.assertEqual(response.status_code, 200)
        response = self.create_state(speed=-5000)
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