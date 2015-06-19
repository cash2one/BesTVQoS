from django import forms

class FileForm(forms.Form):
    name = forms.CharField(max_length = 30)
    date = forms.CharField(max_length = 30)
    content = forms.FileField()