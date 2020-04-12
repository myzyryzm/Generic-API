from django.urls import path, re_path
from general import views

app_name = 'general'

urlpatterns = [
    re_path(r'^index/$', views.index, name='index'),
    re_path(r'^songs/$', views.songs, name='songs')
]