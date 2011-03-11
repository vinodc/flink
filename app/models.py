from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import *

from decimal import *

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
class Profile(CommonInfo):
    user = models.OneToOneField(User, primary_key=True)

    def __unicode__(self):
        if self.user_set.count() == 0:
            return ''
        else:
            return self.user

class Posterboard(CommonInfo):
    title = models.CharField('title', max_length=250)
    is_private = models.BooleanField('private', default=False)
    user = models.ForeignKey(User, editable=False)
    
    # Regarding display on the User Home Page (UHP).
    # Each set is a set of posterboards starting from 1 onwards and control
    # which posterboards are displayed on the home page at any given time.
    display_set = models.IntegerField(blank=True, null=True, default=None)
    # Display position of posterboard in set.
    display_position = models.IntegerField(blank=True, null=True, default=None)
    # Get size of snapshot (in grid blocks AxB). Don't store this
    # in snapshot ImageField.
    snapshot_width = models.IntegerField(default=1)
    snapshot_height = models.IntegerField(default=1)
    # Eventually use "from django.core.files.storage import default_storage"
    # at https://bitbucket.org/david/django-storages/wiki/Home
    snapshot = models.ImageField(upload_to='pbsnapshots', max_length=255, blank=True, null=True)

    def __unicode__(self):
        return self.title

class PBElement(CommonInfo):
    title = models.CharField('title', max_length=250)
    posterboard = models.ForeignKey(Posterboard, editable=False)

    def clean(self):
        if self.state_set.count() == 0:
            raise ValidationError('A posterboard element must be associated'+
                                  'with a state.')
    def __unicode__(self):
       return self.title

class State(CommonInfo):
    pb_element = models.ForeignKey(PBElement, verbose_name='posterboard element')
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

class ImageState(CommonInfo):
    state = models.OneToOneField(State, primary_key=True)
    path = models.ImageField(upload_to='images', max_length=255)
