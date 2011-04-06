import datetime
from django import forms
from django.forms import ModelForm
from app.models import *
        
class BlogSettingsForm(ModelForm):
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

class TextStateForm(ModelForm):
    class Meta:
        model = TextState
        
class AudioStateForm(ModelForm):
    class Meta:
        model = AudioState

class VideoStateForm(ModelForm):
    class Meta:
        model = VideoState
