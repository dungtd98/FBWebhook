from django.urls import path
from .views import TelegramBotApiView, ViberBotApiView
urlpatterns = [
    path('api/tele-bot/', TelegramBotApiView.as_view(), name='tele-bot'),
    path('api/viber-bot/', ViberBotApiView.as_view(), name='viber-bot')
]

