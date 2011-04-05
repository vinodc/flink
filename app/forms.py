import datetime
from django import forms
from django.forms import ModelForm
from app.models import *
        
class BlogSettingsForm(forms.Form):
    grid_size = models.IntegerField()
    class Meta:
        model = BlogSettings

class PosterboardForm(ModelForm):
    class Meta:
        model = Posterboard

class ElementForm(ModelForm):
    class Meta:
        model = Element

class StateForm(ModelForm):
    class Meta:
        model = State

class ImageStateForm(ModelForm):
    class Meta:
        model = ImageState
        
# TODO: create rest of the forms.
