"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from myproject import views

app_name = 'myproject'
admin.site.site_header = 'Group 3 Admin'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name = 'homepage'),
    path('register', views.register_request, name = 'register'),
    path('login', views.login_request, name = 'login'),
    path('logout', views.logout_request, name = 'logout'),
    path('post/', views.post_request, name = 'post'),
    path('post/<int:pk>', views.post_view, name ='post-detail'),
    path('search/', views.search, name = 'search'),
    path('inbox/', views.inbox, name = 'inbox'),
    path('inbox/create-convo', views.convo_request, name='create-convo'),
    path('inbox/<int:pk>/', views.convo_view, name='convo'),
    path('inbox/<int:pk>/create-dm/', views.createDM, name='create-dm'),
    path('weather/', views.weather),
    path('feed/', views.myFeed, name='home-feed'),
    path("followToggle/<str:aut>/",views.followToggle, name="followToggle"),
    path("explore/",views.spotify, name="explore"),
    path("spotifyRender/<str:link>/",views.spotifyRender, name="spotifyRender")
]
