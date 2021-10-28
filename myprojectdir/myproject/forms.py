from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, Comment

# Create your forms here.

class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
  
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class new_post(forms.ModelForm):
    content = forms.CharField(required=True)
    #media = forms.ImageField(required=False)

    class Meta:
        model = Post
        fields = ['title', 'content', 'media']

    def save(self, commit=True):
        user = super(new_post, self).save(commit=False)
        user.content = self.cleaned_data['content']

        if commit:
            user.save()
        return user

class new_comment(forms.ModelForm):
    content = forms.CharField(required=True)

    class Meta:
        model = Comment
        fields = ['content']

    def save(self, commit=True):
        user = super(new_comment, self).save(commit=False)
        user.content = self.cleaned_data['content']

        if commit:
            user.save()
        return user

'''
This python program is designed to to take new registration infomation from user registration page.
Made by: Deep Jain
'''
