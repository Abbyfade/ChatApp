from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.chat_list_view, name='base'),
    path('user_list/', views.user_list, name='user_list'),
    path('chat/start/<str:username>/', views.start_chat, name='start_chat'),
    path('chat/<int:room_id>/', views.chat, name='chat'),
    path('signup/', views.authView, name="authView"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name='logout'),
]
