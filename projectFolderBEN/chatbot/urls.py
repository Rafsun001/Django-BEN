from django.urls import path
from . import views  # Import your views here

urlpatterns = [
    path('get_all_chat/', views.get_all_chat, name='get_all_chat'),
    path('create_chat/', views.create_chat, name='create_chat'),
    path('conversation/', views.conversation, name='conversation'),
    path('get_chat_history/', views.get_chat_history, name='get_chat_history')


]