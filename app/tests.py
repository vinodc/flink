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
from selenium import selenium
import os, time, coverage, unittest, re

import threading

import urllib



from django.core.servers import basehttp 

from django.core.handlers.wsgi import WSGIHandler 

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
- Create two new Posterboard with the same title
- Delete a non-existing Posterboard
- Access a non-existing PosterBoard
- Create a new Posterbaord without a blogger
"""

class PosterboardHandlerTest (TestCase):
    fixtures = ['test_fixture.json']
    
    def setUp(self):        
        [self.c, self.user] = login_user('test','test')
        [self.c1, self.user1] = login_user('ted','ted')
        self.homepath = '/people/'+self.user.username+'/posterboards/'
        self.title = 'testposterboardpost'
    
    def create_posterboard_general(self, title='', private=False, is_user_home_page=False):
        data = {
            'title': title,
            'private': private,
            'is_user_home_page': is_user_home_page,
        }
        response = self.c.post(self.homepath[:-1]+'.json',data)
        return response
    
    def create_posterboard(self, title, private):
        return self.create_posterboard_general(title=title, private=private)

    def delete_posterboard(self, path):
        data = {
            '_action':'delete'
        }
        response = self.c.get(self.homepath+str(path)+'/.json',data)
        return response
    
    def test_create_delete_one_posterboard(self):
        response = self.create_posterboard(self.title, False)
        container = eval(response._container[0])
        self.assertEqual(response.status_code, 200)
        pb_id = container['posterboard-id']
        pb_path = container['posterboard-path']
        
        self.assertEqual(self.title,Posterboard.objects.get(pk=pb_id).title)
        self.assertEqual(self.delete_posterboard(pb_path).status_code, 200)
        self.assertEqual(len(Posterboard.objects.filter(pk=pb_id)), 0)
    
    def test_create_posterboard_bad_title(self):
        title = 'four'
        response = self.create_posterboard(title, False)
        self.assertEqual(response.status_code, 400)
        title = 'new'
        response = self.create_posterboard(title, False)
        self.assertEqual(response.status_code, 400)
    
    def test_create_bad_user_home_page(self):
        title = 'userhomepage'
        response = self.create_posterboard(title, False)
        self.assertEqual(response.status_code, 400)
        title = 'userhomepage123'
        response = self.create_posterboard(title, False)
        self.assertEqual(response.status_code, 400)
    
    def test_get_first_home_page(self):
        self.user.posterboard_set.filter(is_user_home_page=True).delete()
        uhpc = self.user.posterboard_set.filter(is_user_home_page=True).count()
        self.assertEqual(uhpc, 0, 'There aren\'t any user home pages.')
        
        response = self.c.get('/people/'+self.user.username+'.json',{})
        self.assertEqual(response.status_code, 200)
        uhpc = self.user.posterboard_set.filter(is_user_home_page=True).count()
        self.assertEqual(uhpc, 1, 'There shoudl be one user home page now.')
        self.user.posterboard_set.filter(is_user_home_page=True).delete()
    
    def test_create_delete_one_user_home_page(self):
        response = self.create_posterboard_general(is_user_home_page=True)
        container = eval(response._container[0])
        self.assertEqual(response.status_code, 200, container)
        pb_id = container['posterboard-id']
        pb_path = container['posterboard-path']
        
        self.assertEqual(Posterboard.objects.get(pk=pb_id).is_user_home_page, True)
        self.assertRegexpMatches(pb_path, r'^userhomepage-\d+$', 'User home page title malformed: ' + pb_path)
        self.assertEqual(self.delete_posterboard(pb_path).status_code, 200)
        self.assertEqual(len(Posterboard.objects.filter(pk=pb_id)), 0)
    
    def test_create_two_posterboard(self):
        response = self.create_posterboard(self.title, False)
        self.assertEqual(response.status_code, 200)
        # Second one should fail
        response = self.create_posterboard(self.title, False)
        self.assertEqual(response.status_code, 400)
    
    def test_delete_void_posterboard(self):
        response = self.delete_posterboard('void_no_posterboard')
        self.assertEqual(response.status_code, 400)

    def test_access_void_posterboard(self):
        response = self.c.get(self.homepath+'void_posterboard/.json')
        self.assertEqual(response.status_code, 400)
    
    def test_create_posterboard_without_log_in(self):
        self.c.logout()
        response = self.create_posterboard(self.title, False)
        self.assertEqual(response.status_code, 400)
       
    def test_public_posterboard(self):
        response = self.create_posterboard(self.title, False)
        container = eval(response._container[0])
        self.assertEqual(response.status_code, 200)
        pb_id = container['posterboard-id']
        pb_path = container['posterboard-path']
        
        # Everyone can see the posterboard on the home page
        home_page_pbs = self.c.get(self.homepath[:-1]+'.json')._container['pb_ids']
        self.assertTrue(pb_id in home_page_pbs)
        home_page_pbs = self.c1.get(self.homepath[:-1]+'.json')._container['pb_ids']
        self.assertTrue(pb_id in home_page_pbs)
        
        # Everyone can look at the posterboard page
        pb_page = self.c.get(self.homepath+str(pb_path)+'/.json')
        self.assertEqual(pb_page.status_code, 200)
        pb_page = self.c1.get(self.homepath+str(pb_path)+'/.json')
        self.assertEqual(pb_page.status_code, 200)
    
    def test_private_posterboard(self):
        response = self.create_posterboard(self.title, True)
        container = eval(response._container[0])
        self.assertEqual(response.status_code, 200)
        pb_id = container['posterboard-id']
        pb_path = container['posterboard-path']
        
        # Only I can see the posterboard on the home page
        home_page_pbs = self.c.get(self.homepath[:-1]+'.json')._container['pb_ids']
        self.assertTrue(pb_id in home_page_pbs)        
        # Other people cannot see it
        home_page_pbs = self.c1.get(self.homepath[:-1]+'.json')._container['pb_ids']
        self.assertTrue(not pb_id in home_page_pbs)
        
        # Only I can look at the posterboard page
        pb_page = self.c.get(self.homepath+str(pb_path)+'/.json')
        self.assertEqual(pb_page.status_code, 200)
        # Access Denied
        pb_page = self.c1.get(self.homepath+str(pb_path)+'/.json')
        self.assertEqual(pb_page.status_code, 403)
        
             
"""
List of Tests for Element Handler
# Normal Behavior Test
- Create and store an image element with good parameters, then Delete it
- Create and store an text element with good parameters, then Delete it
- Create an image element, update the alt text, and verify that the change took place
- Create an text element, update the content, and verify that the change took place
- Create an element, update the state properties, and verify that the change took place

# Bad Behavior Test
- Create an element object with invalid type
- Create an element with type='image' but do not provide correct image parameter
- Create and store an element without logging in

# Good and Bad Behavior Test
- Create a state with orientation
- Create a state with opacity
- Create a state with delay time
- Create a state with speed
- Create a state with width
- Create a state with height
"""
class ElementHandlerTest (TestCase):
    fixtures = ['test_fixture.json']
    
    def setUp(self):
        settings.VIDEO_CONVERT_SYNC = True
        
        [self.c, self.user] = login_user('test','test')
        self.pb = Posterboard.objects.filter(user__username=self.user.username)[0]
        self.uhp = Posterboard.objects.filter(user__username=self.user.username, is_user_home_page=True)[0]
        self.pbpath = '/people/'+self.user.username+'/posterboards/'+self.pb.title_path+'/elements/'
        self.uhppath = '/people'+self.user.username+'/posterboards/'+self.uhp.title_path+'/elements/'

        # Set paths to files.
        self.imagepath = os.path.join(settings.TEST_MEDIA_ROOT,'mountains.jpg')
        self.videopath = os.path.join(settings.TEST_MEDIA_ROOT,'test-video.ogv')
        self.videotoconvertpath = os.path.join(settings.TEST_MEDIA_ROOT,'SUMMER.MPG')
        self.audiopath = os.path.join(settings.TEST_MEDIA_ROOT,'shimmer.wav')
        
    
    def create_image(self, homepage=False):
        img = open(self.imagepath,'rb')
        data = {
            'element-type':'image',
            'image':img
        }
        if(homepage):
            response = self.c.post(self.uhppath[:-1]+'.json',data)
        else:
            response = self.c.post(self.pbpath[:-1]+'.json',data)
        img.close()
        return response
    
    def create_video(self):
        video = open(self.videopath,'rb')
        data = {
            'element-type':'video',
            'video':video
        }
        response = self.c.post(self.pbpath[:-1]+'.json',data)
        video.close()
        return response

    def create_video_to_convert(self):
        video = open(self.videotoconvertpath,'rb')
        data = {
            'element-type':'video',
            'video':video
        }
        response = self.c.post(self.pbpath[:-1]+'.json',data)
        video.close()
        return response

    def create_audio(self):
        audio = open(self.audiopath,'rb')
        data = {
            'element-type':'audio',
            'audio':audio
        }
        response = self.c.post(self.pbpath[:-1]+'.json',data)
        audio.close()
        return response

    def update_image_wrapper(self, state_id, alt):
        image = ImageState.objects.get(pk=state_id)
        beforeUpdateURL = image.image.url
        h = image.state.position_height + 1
        w = image.state.position_width + 1
        
        data = {
            '_action':'put',
            'element-type':'image',
            'state-id': state_id,
            'child-id': state_id,
            'image-alt': alt,
            'state-position_height': h,
            'state-position_width': w,
        }
        response = self.c.post(self.pbpath[:-1]+'.json',data)
        image = ImageState.objects.get(pk=state_id)
        state = image.state
        self.assertEqual(h, state.position_height)
        self.assertEqual(w, state.position_width)
        self.assertEqual(beforeUpdateURL,image.image.url)
        self.assertEqual(alt,image.alt)
        
    def update_video_wrapper(self, state_id):
        video = VideoState.objects.get(pk=state_id)
        beforeUpdateUpdatedAt = video.updated_at
        beforeUpdateCreatedAt = video.created_at
        h = video.state.position_height + 1
        w = video.state.position_width + 1
        
        data = {
            '_action':'put',
            'element-type':'video',
            'state-id': state_id,
            'child-id': state_id,
            'state-position_height': h,
            'state-position_width': w,
        }
        response = self.c.post(self.pbpath[:-1]+'.json',data)
        video = VideoState.objects.get(pk=state_id)
        state = video.state
        self.assertEqual(h, state.position_height)
        self.assertEqual(w, state.position_width)
        self.assertEqual(video.created_at, beforeUpdateCreatedAt)
        
    def update_audio_wrapper(self, state_id):
        audio = AudioState.objects.get(pk=state_id)
        beforeUpdateUpdatedAt = audio.updated_at
        beforeUpdateCreatedAt = audio.created_at
        h = audio.state.position_height + 1
        w = audio.state.position_width + 1
        
        data = {
            '_action':'put',
            'element-type':'audio',
            'state-id': state_id,
            'child-id': state_id,
            'state-position_height': h,
            'state-position_width': w,
        }
        
        response = self.c.post(self.pbpath[:-1]+'.json',data)
        audio = AudioState.objects.get(pk=state_id)
        state = audio.state
        self.assertEqual(h, state.position_height)
        self.assertEqual(w, state.position_width)
        self.assertEqual(audio.created_at, beforeUpdateCreatedAt)

    def create_text(self):
        data = {
            'element-type':'text',
            'text-content':'This is a test text line.'
        }
        response = self.c.post(self.pbpath[:-1]+'.json',data)
        return response

    def update_text_wrapper(self, state_id, content):
        data = {
            '_action':'put',
            'element-type':'text',
            'child-id': state_id,
            'text-content': content
        }
        response = self.c.post(self.pbpath[:-1]+'.json',data)
        text = TextState.objects.get(pk=state_id)
        self.assertEqual(content,text.content)
    
    def create_state(self, property):
        data = {
            'element-type':'text',
            'text-content':'This is a test text line'
        }
        
        for key in property.keys():
            data['state-'+key] = property[key]
            
        response = self.c.post(self.pbpath[:-1]+'.json',data)
        return response
    
    def update_state_wrapper(self, state_id, property):
        data = {
            '_action':'put',
            'state-id': state_id,
        }
        
        for key in property.keys():
            data['state-'+key] = property[key]

        response = self.c.post(self.pbpath[:-1]+'.json',data)
        state = State.objects.get(pk=state_id)
        for key in property.keys():
            val = eval('state.'+key)
            self.assertEqual(property[key],val)
    
    def delete_element(self, id, homepage=False):
        data = {
            '_action':'delete'
        }
        if(homepage):
            response = self.c.get(self.uhppath+str(id)+'/.json',data)
        else:
            response = self.c.get(self.pbpath+str(id)+'/.json',data)
        return response
    
    def delete_state(self, response):
        id = eval(response._container[0])['element-id']
        return self.delete_element(id)    
        
    def test_create_delete_one_image(self):
        response = self.create_image()
        container = eval(response._container[0])
        self.assertEqual(response.status_code, 200)
        element_id = container['element-id']
        self.assertEqual(self.pb.title,Element.objects.get(pk=element_id).posterboard.title)
        self.assertEqual(self.delete_element(element_id).status_code, 200)
        self.assertEqual(len(Element.objects.filter(pk=element_id)), 0)
    
    def test_create_delete_one_video(self):
        response = self.create_video()
        container = eval(response._container[0])
        self.assertEqual(response.status_code, 200)
        element_id = container['element-id']
        self.assertEqual(self.pb.title,Element.objects.get(pk=element_id).posterboard.title)
        self.assertEqual(self.delete_element(element_id).status_code, 200)
        self.assertEqual(len(Element.objects.filter(pk=element_id)), 0)

    def test_create_delete_one_video_to_convert(self):
        response = self.create_video_to_convert()
        container = eval(response._container[0])
        self.assertEqual(response.status_code, 200)
        element_id = container['element-id']
        self.assertEqual(self.pb.title,Element.objects.get(pk=element_id).posterboard.title)
        self.assertEqual(self.delete_element(element_id).status_code, 200)
        self.assertEqual(len(Element.objects.filter(pk=element_id)), 0)

    def test_create_delete_one_audio(self):
        response = self.create_audio()
        container = eval(response._container[0])
        self.assertEqual(response.status_code, 200)
        element_id = container['element-id']
        self.assertEqual(self.pb.title,Element.objects.get(pk=element_id).posterboard.title)
        self.assertEqual(self.delete_element(element_id).status_code, 200)
        self.assertEqual(len(Element.objects.filter(pk=element_id)), 0)

    def test_create_delete_one_text(self):
        response = self.create_text()
        container = eval(response._container[0])
        self.assertEqual(response.status_code, 200)
        element_id = container['element-id']
        self.assertEqual(self.pb.title,Element.objects.get(pk=element_id).posterboard.title)
        self.assertEqual(self.delete_element(element_id).status_code, 200)
        self.assertEqual(len(Element.objects.filter(pk=element_id)), 0)        
        
    def test_update_one_image(self):
        response = self.create_image()
        container = eval(response._container[0])
        self.assertEqual(response.status_code, 200)
        element_id = container['element-id']
        state_id = container['state-id']
        self.assertEqual(self.pb.title,Element.objects.get(pk=element_id).posterboard.title)
        
        self.update_image_wrapper(state_id,'test alt')
        
        self.assertEqual(self.delete_element(element_id).status_code, 200)
        self.assertEqual(len(Element.objects.filter(pk=element_id)), 0) 
        self.assertEqual(len(ImageState.objects.filter(pk=state_id)), 0) 
        
    def test_update_one_video(self):
        response = self.create_video()
        container = eval(response._container[0])
        self.assertEqual(response.status_code, 200)
        element_id = container['element-id']
        state_id = container['state-id']
        self.assertEqual(self.pb.title,Element.objects.get(pk=element_id).posterboard.title)
        
        self.update_video_wrapper(state_id)
        
        self.assertEqual(self.delete_element(element_id).status_code, 200)
        self.assertEqual(len(Element.objects.filter(pk=element_id)), 0) 
        self.assertEqual(len(VideoState.objects.filter(pk=state_id)), 0)
        
    def test_update_one_audio(self):
        response = self.create_audio()
        container = eval(response._container[0])
        self.assertEqual(response.status_code, 200)
        element_id = container['element-id']
        state_id = container['state-id']
        self.assertEqual(self.pb.title,Element.objects.get(pk=element_id).posterboard.title)
        
        self.update_audio_wrapper(state_id)
        
        self.assertEqual(self.delete_element(element_id).status_code, 200)
        self.assertEqual(len(Element.objects.filter(pk=element_id)), 0) 
        self.assertEqual(len(AudioState.objects.filter(pk=state_id)), 0)
    
    def test_update_one_text(self):
        response = self.create_text()
        container = eval(response._container[0])
        self.assertEqual(response.status_code, 200)
        element_id = container['element-id']
        state_id = container['state-id']
        self.assertEqual(self.pb.title,Element.objects.get(pk=element_id).posterboard.title)
        
        self.update_text_wrapper(state_id,'Modified Test line')
        
        self.assertEqual(self.delete_element(element_id).status_code, 200)
        self.assertEqual(len(Element.objects.filter(pk=element_id)), 0) 
        self.assertEqual(len(TextState.objects.filter(pk=state_id)), 0)
    
    def test_update_state(self):
        old_property = {'orientation':0, 'delay':0}
        response = self.create_state(old_property)
        container = eval(response._container[0])
        self.assertEqual(response.status_code, 200)
        state_id = container['state-id']
    
        new_property = {'orientation':150, 'delay':1.0}    
        self.update_state_wrapper(state_id, new_property)

        self.assertEqual(self.delete_state(response).status_code, 200)
        self.assertEqual(len(State.objects.filter(pk=state_id)), 0) 
    
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
    
    def test_create_state_good_bad_orientation(self):
        property = {'orientation':180}
        response = self.create_state(property)
        self.assertEqual(response.status_code, 200)
        self.delete_state(response)
        property = {'orientation':360}
        response = self.create_state(property)
        self.assertEqual(response.status_code, 400)
            
    def test_create_state_good_bad_opacity(self):
        property = {'opacity':0.5}
        response = self.create_state(property)
        self.assertEqual(response.status_code, 200)
        self.delete_state(response)
        property = {'opacity':2.0}
        response = self.create_state(property)
        self.assertEqual(response.status_code, 400)
        
    def test_create_state_good_bad_delay_time(self):
        property = {'delay':1.0}
        response = self.create_state(property)
        self.assertEqual(response.status_code, 200)
        self.delete_state(response)
        property = {'delay':-1.0}
        response = self.create_state(property)
        self.assertEqual(response.status_code, 400)
        
    def test_create_state_good_bad_speed(self):    
        property = {'speed':5000}
        response = self.create_state(property)
        self.assertEqual(response.status_code, 200)
        self.delete_state(response)
        property = {'speed':-5000}
        response = self.create_state(property)
        self.assertEqual(response.status_code, 400)
        
    def tearDown(self):
        #os.remove(self.imagepath)
        pass

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

'''
# Normal Behavior Test
- Check that username corresponds with the current user. If so, we no the right BlogSettings object
    is being accessed.

# Bad Behavior Test

'''
class TestSettings(TestCase):
    fixtures = ['test_fixture.json']
     
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*firefox", "http://localhost:8000/")
        self.selenium.start()
    
    def test_settings(self):
        sel = self.selenium
        sel.open("/")
        sel.click("link=Login")
        sel.wait_for_page_to_load("30000")
        sel.type("id_email", "test@test.com")
        sel.type("id_password", "test")
        sel.click("id_remember")
        sel.click("id_remember")
        sel.click("//button[@type='submit']")
        sel.wait_for_page_to_load("30000")
        sel.click("link=Settings")
        sel.wait_for_page_to_load("30000")
        sel.click("//input[@value='Edit Settings']")
        sel.wait_for_page_to_load("30000")
        sel.select("id_grid_size", "label=Grid Size 3")
        sel.click("//input[@value='Submit']")
        sel.wait_for_page_to_load("30000")
        sel.click("//input[@value='Edit Settings']")
        sel.wait_for_page_to_load("30000")
        sel.select("id_grid_size", "label=Grid Size 4")
        sel.click("//input[@value='Submit']")
        sel.wait_for_page_to_load("30000")
        self.failUnless(sel.is_text_present("New grid size is: 4"))
        self.failUnless(sel.is_text_present("old gridsize : 3"))
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)
