# bot.urls.py

from django.urls import path
from django.contrib import admin

from .views import (
    MessengerView,
    PageMessageViewV2
    )

app_name ='bot_webhooks'
urlpatterns = [
    path('webhook', MessengerView.as_view(), name='webhook'),
    path('v2/webhook', PageMessageViewV2.as_view(), name='webhookv2')
]

