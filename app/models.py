from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import *

from decimal import *
from app.lib import *

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

    class Meta:
        abstract = True

# This is the profile for users. Use the get_profile() method provided by
# the User model to get this.
# http://docs.djangoproject.com/en/dev/topics/auth/#storing-additional-information-about-users
# This represents a blog.
class Profile(CommonInfo):
    user = models.OneToOneField(User, primary_key=True)

    @models.permalink
    def get_absolute_url(self):
        return ('profile', (self.user))

    def __unicode__(self):
        if self.user_set.count() == 0:
            return ''
        else:
            return self.user

class BlogSettings(CommonInfo):
    user = models.OneToOneField(User, primary_key=True, verbose_name='user')
    blog_title = models.CharField(max_length=250, default='My Blog')
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
    
    @models.permalink
    def get_absolute_url(self):
        return ('posterboard_url', (), {
                    'blogger': self.user.username, 
                    'posterboard': self.title_path,
                    'format':'html'})

ELEMENT_TYPE_CHOICES = (('I','image'),('A','audio'),('V','video'),('T','text'))
class PBElement(CommonInfo):
    # title = models.CharField('title', max_length=250, blank = True)
    type = models.CharField(max_length=1, choices=ELEMENT_TYPE_CHOICES, editable=False)
    posterboard = models.ForeignKey(Posterboard, editable=False)

    def clean(self):
        if self.state_set.count() == 0:
            raise ValidationError('A posterboard element must be associated'+
                                  'with a state.')
    def __unicode__(self):
       return self.title

class State(CommonInfo):
    pb_element = models.ForeignKey(PBElement, verbose_name='posterboard element')
    # Specify the type of the state
    # Position WxH is a factor of grid size.
    position_width = models.IntegerField(default=1)
    position_height = models.IntegerField(default=1)
    #Orientation is between 0 and 359 degrees.
    orientation = models.IntegerField(default=0, 
                                      validators = [
                                          MaxValueValidator(359),
                                          MinValueValidator(0)
                                      ])
    opacity = models.DecimalField(max_digits=3, 
                                  decimal_places=2, 
                                  default=1.00, 
                                  validators=[
                                      MaxValueValidator(Decimal('1.00')),
                                      MinValueValidator(Decimal('0.00'))
                                  ])
    # Time before this state occurs.
    delay = models.FloatField(default=0.0, 
                              validators = [
                                  MinValueValidator(0.0)
                              ])
    # Speed of transition into this state in milliseconds.
    speed = models.IntegerField(default=400,
                                validators = [
                                    MinValueValidator(1),
                                    MaxValueValidator(10000)
                                ])
    
    def clean(self):
        if self.delay is None: self.delay = 0.0
        if self.speed is None: self.speed = 400
        if self.opacity is None: self.opacity = 1.00
        if self.orientation is None: self.orientation = 0
        if self.position_width is None: self.position_width = 1
        if self.position_height is None: self.position_height = 1 
        
class ImageState(CommonInfo):
    state = models.OneToOneField(State, primary_key=True)
    alt = models.CharField('alt', max_length=250, blank = True)
    image = models.ImageField(upload_to='images', max_length=255)
