from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import NewUserForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.views import View
from .forms import new_post, new_comment
import datetime, requests
from django.views.generic.list import ListView
from .models import Post, Comment, Message
from django.db import connection
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest



def home(request):    
    data = Post.objects.exclude(censor=1)
    data = data.reverse()

    pst = {
        "title" : data
    }

    return render(request, "base.html", pst)

def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect(home)
        messages.error(request, form.errors)
    form = NewUserForm()
    return render(request=request, template_name='../templates/register.html', context={'register_form':form})

def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect(home)
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="../templates/login.html", context={"login_form":form})

def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect(home)

def post_request(request):
    if request.method == "POST":
        form = new_post(request.POST) #request.FILES)
        if form.is_valid():
            np = form.save(commit=False)
            np.author = request.user
            np.save()
            messages.success(request, "Posted Successfully!")
            return redirect(home)
        messages.error(request, form.errors)
    form = new_post()

    return render(request=request, template_name='../templates/post.html', context={"post_form":form})

def post_view(request,pk):

    if(request.GET.get('mybtn')):
        query = "UPDATE myproject_post SET censor = TRUE WHERE id = " + str(pk)
        cursor = connection.cursor()
        cursor.execute(query)
        messages.success(request, "CENSOR SUCCESS")

    post = Post.objects.get(pk=pk)
    form = new_comment(request.POST)
    
    if form.is_valid():
        cp = form.save(commit=False)
        cp.author_id = request.user
        cp.post = post
        cp.save()
        messages.success(request, "Commented Successfully!")

    comments = Comment.objects.all()
    
    context = {
        'post':post,
        "comment_form":form,
        "comments":comments
    }

    return render(request, "../templates/post_detail.html", context)

def search(request):
    data = Post.objects.all()

    if request.method == "POST":
        searched = request.POST['searched']

        userData = Post.objects.none()

        try:
            potential_user_id = User.objects.get(username=searched).pk
            userData = Post.objects.filter(author_id=potential_user_id)
        except Exception:
            pass

        searchData = Post.objects.filter(title__icontains=searched) 

        allDat = searchData | userData
        return render(request, "../templates/search.html", {'searched' : searched, 'data' : allDat, 'allData' : data})
    else:
        return render(request, "../templates/search.html")

def getWriter(author_id):
    user = User.objects.get(id=author_id)
    return(user)

def weather(request):
    url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=271d1234d3f497eed5b1d80a07b3fcd1"
    city = 'Newark'

    r = requests.get(url.format(city)).json()

    city_weather = {
        'city' : city,
        'temperature' : r['main']['temp'],
        'descrition' : r['weather'][0]['description'],
        'icon' : r['weather'][0]['icon'],
    }

    context = {'city_weather' : city_weather}

    return render(request, "../templates/weather.html", context)

@login_required
def inbox(request):
    dmessages = Message.get_messages(user=request.user)
    active_direct = None
    directs = None

    if dmessages:
        message = dmessages[0]
        active_direct = message['user'].username
        directs = Message.objects.filter(user=request.user, recipient=message['user'])
    for message in dmessages:
        if message['user'].username == active_direct:
            message['unread'] = 0
    context = {
        'directs': directs,
        'messages': dmessages,
        'active_direct': active_direct,
    }
    return render(request, "../templates/conversations.html", context)

@login_required
def directs(request, username):
	user = request.user
	messages = Message.get_messages(user=request.user)
	active_direct = username
	directs = Message.objects.filter(user=request.user, recipient_username=username)
	context = {
			'directs': directs,
			'dmessages': messages,
			'active_direct': active_direct,
		}
		
	return render(request=request, template_name="../templates/conversations.html", context=context)

#in urls.py it should be path('send/', SendDirect, name='send_direct')
#in whatever.html please add <form tole="form" methods="POST" action="{{%url 'send_direct' %}}">
#and also {% crsf_token %}
@login_required
def send_direct(request):
	from_user = request.user
	to_user_username = request.POST.get('to_user')
	content = request.POST.get('body')
	
	if request.method == 'POST':
		to_user = User.objects.get(username = to_user_username)
		Message.send_message(from_user, to_user, content)
		return redirect('conversations')
	else:
		HttpResponseBadRequest()