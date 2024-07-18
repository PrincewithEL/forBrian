from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('Home/', views.Home, name='Home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('send/', views.send_message, name='send_message'),
    path('receive/', views.receive_message, name='receive_message'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('service/', views.service, name='service'),
]