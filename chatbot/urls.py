from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chatbot_ui, name='chatbot_ui'),
    path('send/', views.send_message, name='send_message'),
    path('get-response/', views.get_bot_response, name='get_response'),
    path('symptom-checker/', views.symptom_checker, name='symptom_checker'),
    path('check-symptoms/', views.check_symptoms, name='check_symptoms'),
    path('clear-session/', views.clear_session, name='clear_session'),
]