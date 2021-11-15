from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import NewUserForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.views import View
from .forms import new_post, new_comment, new_convo, new_DM
import datetime, requests
from django.views.generic.list import ListView
from .models import Post, Comment, Conversations, Message, suscription
from django.db import connection
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def home(request):    
    data = Post.objects.exclude(censor=1)
    data = data.reverse()
    currentUser = request.user
    
    # secondHalf = track_id.split(".com/",1)[1]
    # firstHalf = track_id.split('track')[0]
    # emlink = firstHalf+"embed/" + secondHalf
    # context = {
    # 'result':track,
    # 'embedlink':emlink,
    #     "tracks" : tracks
    # }
    try:
        user = User.objects.get(username=currentUser).pk
        userSuscriptionData = suscription.objects.get(user_id=user)
        susc = userSuscriptionData.suscriptions
        susc = str(susc)
        pst = {
            "title" : data,
            "sus" : susc,
        }
        return render(request, "base.html", pst)
    except:
        pass

    pst = {
        "title" : data,
        "sus": ""
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
            if np.spotifyLink != "":
                secondHalf = np.spotifyLink.split(".com/",1)[1]
                firstHalf = np.spotifyLink.split('track')[0]
                emlink = firstHalf+"embed/" + secondHalf
                np.embedSpotifyLink = emlink
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
    
    try:
        currentUser = request.user
        user = User.objects.get(username=currentUser).pk
        userSuscriptionData = suscription.objects.get(user_id=user)
        susc = userSuscriptionData.suscriptions
        susc = str(susc)
    except:
        susc = ""
    
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
        "comments":comments,
        "sus" : susc
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
    convos = Conversations.objects.filter(Q(user1=request.user) | Q(user2=request.user))#filter this to get queries that only involve with user
    context = {
        'convos': convos
    }
    return render(request, "../templates/inbox.html", context)

@login_required
def convo_request(request):
    if request.method == "POST":
        form = new_convo(request.POST)
        username = request.POST.get('username')
        try:
            user2 = User.objects.get(username=username)
            if Conversations.objects.filter(user1=request.user, user2=user2).exists(): #makes sure that the user exists in database
                convo = Conversations.objects.filter(user1=request.user, user2=user2)[0]#grabs first conversation between 2 users
                return redirect('convo', pk=convo.pk)
            elif Conversations.objects.filter(user1=user2, user2=request.user).exists():
                convo = Conversations.objects.filter(user1=user2, user2=request.user)[0]
                return redirect('convo', pk=convo.pk)
            if form.is_valid():#if convo does not exist, make new
                sender_convo = Conversations(
                    user1=request.user,
                    user2=user2
                )
                sender_convo.save()
                convo_pk = sender_convo.pk
                return redirect('convo', pk=convo_pk)
        except:
            return redirect('create-convo')
        messages.error(request, form.errors)
    form = new_convo()

    return render(request=request, template_name="../templates/create_convo.html", context={"convo_form":form})

def convo_view(request, pk):
    #if(request.GET.get('mybtn')):
        #query = "UPDATE myproject_conversations SET  ?? = TRUE WHERE id = " + str(pk)
        #cursor = connection.cursor()
        #cursor.execute(query)

    convo= Conversations.objects.get(pk=pk)
    form = new_DM(request.POST)
    
    dm_list = Message.objects.filter(convo_id__pk__contains=pk)#getting conversation's pk and see if it matches the messages we wanna show
    
    context = {
        'convo':convo,
        'dm_form': form,
        'dm_list': dm_list
    }

    return render(request, "../templates/convo.html", context)

def createDM(request, pk):
    convo = Conversations.objects.get(pk=pk)
    if convo.user2 == request.user:
        user2 = convo.user1
    else:
        user2 = convo.user2
    
    dm = Message(
        convo_id = convo,
        sender = request.user,
        recipient = user2,
        content = request.POST.get('dm'),
    )
    dm.save()
    return redirect('convo', pk=pk)

@login_required
def followToggle(request, aut):
    currentUser = request.user
    try:
        user = User.objects.get(username=currentUser).pk
        userSuscriptionData = suscription.objects.get(user_id=user)

        userSus = userSuscriptionData.suscriptions

        if aut in userSus:
            userSus = userSus.replace(aut, "")
            userSuscriptionData.suscriptions = userSus
            userSuscriptionData.save()
            messages.success(request, "Unsuscribed to User.")
            return redirect('home-feed')
            
        else:
            userSuscriptionData.suscriptions = userSus + aut
            userSuscriptionData.save()
            messages.success(request, "Suscribed to User.")
            return redirect('home-feed')
    except Exception:
        newSus = suscription(suscriptions=aut, user=currentUser)
        newSus.save()

    return redirect('homepage')

def myFeed(request):
    data = Post.objects.exclude(censor=1)
    data = data.reverse()

    currentUser = request.user
    
    try:
        user = User.objects.get(username=currentUser).pk
        userSuscriptionData = suscription.objects.get(user_id=user)
        susc = userSuscriptionData.suscriptions
        susc = str(susc)
    except:
        susc = ""

    pst = {
        "title" : data,
        "sus" : susc
    }

    return render(request, "myfeed.html", pst)

def spotify(request):
        # data = Post.objects.values('spotifyLink')
        # data = data.reverse()

        # for track_id in str(data):
        #     if track_id:
        #         sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="8f5244d9e0ea43948009277c93b62688", client_secret="1e799c3a6a644d669a1f91427ebfb6e2"))
        #         track = sp.track(track_id)
        #         tracks += track

        # # #to generate an embed link
        # # secondHalf = track_id.split(".com/",1)[1]
        # # firstHalf = track_id.split('track')[0]
        # # emlink = firstHalf+"embed/" + secondHalf
        # context = {
        # # 'result':track,
        # # 'embedlink':emlink,
        #     "tracks" : tracks
        # }
        return render(request, "../templates/explore.html")

def spotifyRender(request, link):
    messages.success(request, "Spotify")
    return redirect('homepage')
    



