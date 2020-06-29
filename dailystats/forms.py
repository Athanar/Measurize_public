from django import forms
from django.forms import formset_factory, BaseFormSet

class FirstForm(forms.Form):
    name = forms.CharField(max_length=100)

