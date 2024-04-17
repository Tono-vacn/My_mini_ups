from django import forms
from django.contrib.auth.models import User
from .models import *

class RegForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username','email','password']
        
class ModPlcForm(forms.ModelForm):
    class Meta:
        model = Package_tmp
        fields = ['dst_x','dst_y']
        
class ChangeEmailForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']