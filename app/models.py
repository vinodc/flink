from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import *

from decimal import *
import datetime
from app.lib import *

from videologue.models import VideoModel

def reserved_keywords(value):
    """
    Makes sure the value isn't a reserved word such as 'new',
    which is used in our REST setup.
    """
    reserved = ['new']
    if value in reserved:
        raise ValidationError(u'The identifier cannot be' +
                              u'the reserved word %s' % value)
 
#-------------------------------
#
# Defaults will have to be imported from some kind of settings model later.
# The settings model itself should have these defaults (such as for is_private)
# and then depending on the value there, we can set the default over here.
# Each user should have a settings.
#
#-------------------------------

class CommonInfo(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.pk:
            self.created_at = datetime.datetime.today()
        self.updated_at = datetime.datetime.today()
        super(CommonInfo, self).save(*args, **kwargs)


    class Meta:
        abstract = True

# This is the blog settings object for a given user...so basically just user settings
class BlogSettings(CommonInfo):
    user = models.OneToOneField(User, primary_key=True, verbose_name='user')
    blog_title = models.CharField(max_length=250, default='My Blog')
    
    # The size of the grid
    grid_size = models.IntegerField(default=5, 
    					validators = [
    						MaxValueValidator(5),
    						MinValueValidator(1)
    					])
    					
    # On blog home page, for each set of posterboards:
    # Number of grid blocks wide the set is.
    set_width = models.IntegerField(default=4, 
                                    validators = [
                                         MaxValueValidator(8),
                                         MinValueValidator(1)
                                    ])
    # Number of grid blocks high the set is.
    set_height = models.IntegerField(default=4, 
                                     validators = [
                                          MaxValueValidator(6),
                                          MinValueValidator(1)
                                     ])
    def __unicode__(self):
        return self.blog_title + ' settings'

class Posterboard(CommonInfo):
    title = models.CharField('title', unique=True, max_length=125,
                             validators=[
                                 MinLengthValidator(5),
                                 reserved_keywords])
    # Gets created during validation in clean()
    title_path = models.CharField('title', unique=True, max_length=250,
                                  editable=False)
    private = models.BooleanField('private?', default=False)
    user = models.ForeignKey(User, editable=False)
    
    # Regarding display on the User Home Page (UHP).
    # Each set is a set of posterboards starting from 1 onwards and control
    # which posterboards are displayed on the home page at any given time.
    display_set = models.IntegerField(blank=True, null=True, default=0)
    # Display position of posterboard in set.
    display_position = models.IntegerField(blank=True, null=True, default=0)
    # Get size of snapshot (in grid blocks AxB). Don't store this
    # in snapshot ImageField. This is the grid blocks spanned by the image of this
    # posterboard in the User Home Page.
    snapshot_width = models.IntegerField(blank=True, default=1)
    snapshot_height = models.IntegerField(blank=True, default=1)
    # Eventually use "from django.core.files.storage import default_storage"
    # at https://bitbucket.org/david/django-storages/wiki/Home
    snapshot = models.ImageField(upload_to='pbsnapshots', max_length=255, 
                                 blank=True, null=True)

    def clean(self):
        self.title_path = title_to_path(self.title)
        if len(self.title_path) < 5:
            raise ValidationError('Please enter a longer posterboard title', 
                                   'min_value')
        reserved_keywords(self.title_path)
        if self.snapshot_width is None: self.snapshot_width = 1
        if self.snapshot_height is None: self.snapshot_height = 1 

    def __unicode__(self):
        return self.title
    
    #@models.permalink
    def get_absolute_url(self):
        return '/people/'+ self.user.username +'/posterboards/'+ self.title_path +'/'
        #return ('posterboard_url', (), {
        #            'blogger': self.user.username, 
        #            'posterboard': self.title_path,
        #            'format':'html'})

ELEMENT_TYPE_CHOICES = (('image','image'),('audio','audio'),('video','video'),('text','text'))
class Element(CommonInfo):
    # title = models.CharField('title', max_length=250, blank = True)
    type = models.CharField(max_length=5, choices=ELEMENT_TYPE_CHOICES)
    posterboard = models.ForeignKey(Posterboard, editable=False)

    def __unicode__(self):
       return self.posterboard.title + ' element' + str(self.id)
   
    def delete(self):
        for state in State.objects.filter(pb_element=self):
            state.delete()
        super(Element,self).delete()

class State(CommonInfo):
    pb_element = models.ForeignKey(Element, verbose_name='posterboard element', editable=False)
    # Specify the type of the state
    # Position WxH is a factor of grid size.
    position_x = models.IntegerField(default=1, blank=True)
    position_y = models.IntegerField(default=1, blank=True)
    position_width = models.IntegerField(default=1, blank=True)
    position_height = models.IntegerField(default=1, blank=True)
    #Orientation is between 0 and 359 degrees.
    orientation = models.IntegerField(default=0, 
                                      validators = [
                                          MaxValueValidator(359),
                                          MinValueValidator(0)
                                      ], blank=True)
    opacity = models.DecimalField(max_digits=3, 
                                  decimal_places=2, 
                                  default=Decimal('1.00'), 
                                  validators=[
                                      MaxValueValidator(Decimal('1.00')),
                                      MinValueValidator(Decimal('0.00'))
                                  ], blank=True)
    # Time before this state occurs.
    delay = models.FloatField(default=0.0, 
                              validators = [
                                  MinValueValidator(0.0)
                              ], blank=True)
    # Speed of transition into this state in milliseconds.
    speed = models.IntegerField(default=400,
                                validators = [
                                    MinValueValidator(1),
                                    MaxValueValidator(10000)
                                ], blank=True)
    def delete(self):
        for state in ImageState.objects.filter(state=self):
            state.delete()
        for state in TextState.objects.filter(state=self):
            state.delete()
        for state in AudioState.objects.filter(state=self):
            state.delete()
        for state in VideoState.objects.filter(state=self):
            state.delete()
        super(State,self).delete()
    
    def clean(self):
        if self.delay is None: self.delay = 0.0
        if self.speed is None: self.speed = 400
        if self.opacity is None: self.opacity = Decimal('1.00')
        if self.orientation is None: self.orientation = 0
        if self.position_x is None: self.position_x = 1
        if self.position_y is None: self.position_y = 1
        if self.position_width is None: self.position_width = 1
        if self.position_height is None: self.position_height = 1 
        
class ImageState(CommonInfo):
    state = models.OneToOneField(State, editable=False, primary_key=True)
    alt = models.CharField('alt', max_length=250, blank = True)
    image = models.ImageField(upload_to='images', max_length=255, editable=False)
       
    def delete(self):
        self.image.delete()
        super(ImageState,self).delete()
        
class TextState(CommonInfo):
    state = models.OneToOneField(State, editable=False, primary_key=True)
    content = models.TextField(blank = True)
       

# TODO: create the rest of the <Type>State models.
# Use the same format as above. If you have defaults for anything, be sure to include
# it in a clean() method too, as above.

class VideoState(VideoModel):
    state = models.OneToOneField(State, editable=False, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    
    def save(self, *args, **kwargs):
      ''' On save, update timestamps '''
      if not self.pk:
          self.created_at = datetime.datetime.today()
      self.updated_at = datetime.datetime.today()
      super(VideoState, self).save(*args, **kwargs)
      
    def delete(self):
      # Remove video files?
      super(VideoState, self).delete()
      
    def clean(self):
       return True 
   
    def __unicode__(self):
       return "video"+ str(self.pk)
   
    def __str__(self):
        return self.__unicode__()


class AudioState(CommonInfo):
    state = models.OneToOneField(State, editable=False, primary_key=True)
