from django import forms

class CommentForm(forms.Form):
    username = forms.CharField(label='Your name', max_length=30)
    comment = forms.CharField(label='Comment', max_length=500)