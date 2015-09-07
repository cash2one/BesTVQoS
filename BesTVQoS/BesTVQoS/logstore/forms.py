from django import forms

class FileForm(forms.Form):
    name = forms.CharField(max_length = 255)
    date = forms.CharField(max_length = 255)
    content = forms.FileField()
