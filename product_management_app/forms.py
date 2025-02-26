from django import forms

class NameForm(forms.Form):
    name =forms.CharField( max_length=10)
    address=forms.CharField()