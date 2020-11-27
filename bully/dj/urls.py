# \ <section:top>
from django.contrib import admin
from django.urls import path
from dj import views
# / <section:top>
# \ <section:mid>
urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls, name='admin'),
]
# / <section:mid>
