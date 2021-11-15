from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, Comment, Conversations, Message

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
        fields = ['title', 'content', 'media', 'spotifyLink']

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

class new_convo(forms.Form):
    username = forms.CharField(required=True,max_length=100)

    class Meta:
        model = Conversations
        fields = ['user2']


    '''
    user2 = forms.CharField(required=True)

    class Meta:
        model = Conversations
        fields = ['user2']

    def save(self, commit=True):
        starter = super(new_convo, self).save(commit=False)
        starter.recipient = self.cleaned_data['user2']

        if commit:
            starter.save()
        return starter
    '''
class new_DM(forms.Form):
    dm = forms.CharField(required=False,label='',max_length=1000)

'''
This python program is designed to to take new registration infomation from user registration page.
Made by: Deep Jain
'''
