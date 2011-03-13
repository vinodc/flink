import datetime
from django.forms import ModelForm
from app.models import *

# Not sure if this whole Profile thing is necessary yet.
class ProfileForm(ModelForm):
    class Meta:
        model = Profile

class PosterboardForm(ModelForm):
    class Meta:
        model = Posterboard

class ElementForm(ModelForm):
    class Meta:
        model = PBElement

class StateForm(ModelForm):
    class Meta:
        model = State

class ImageStateForm(ModelForm):
    class Meta:
        model = ImageState