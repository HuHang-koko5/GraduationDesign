"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.conf.urls import url,include
from django.urls import path
from login import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login),
    path('geo/', views.geo_img),
    path('register/', views.register),
    path('index/', views.index),
    url(r'^captcha', include('captcha.urls')),
    path('tweets/', views.tweets),
    path('tweetlist/', views.tweet_detail),
    path('logout/', views.logout),
    url(r'^$', views.index),
    path('geo_echarts/', views.geo_echarts),
    path('si_list/', views.si_list),
    path('si/', views.si_detail),
    path('reference/', views.refer),
    path('timebar/', views.timeBar),
    path('time_echarts/', views.time_distribution)
]
