from django.urls import path
from .views import TelegramBotApiView
urlpatterns = [
    path('tele-bot/', TelegramBotApiView.as_view(), name='tele-bot')
]