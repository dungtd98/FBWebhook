from django.shortcuts import render
from dotenv import load_dotenv
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .tasks import telegram_response_message, viberbot_response_message
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.viber_requests import ViberMessageRequest
import json
load_dotenv('.env')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
VIBER_AUTH_TOKEN = os.environ.get('VIBER_AUTH_TOKEN')
from viberbot.api.messages.text_message import TextMessage

# Create your views here.
class TelegramBotApiView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'detail':'OK'}, status=status.HTTP_200_OK)
    def post(self, request, *args, **kwargs):
        incoming_message = request.data['message']['text']
        chat_id = request.data['message']['chat']['id']
        telegram_response_message.delay(chat_id, incoming_message)
        return Response({'detail':'OK'}, status=status.HTTP_200_OK)

# Viber Bot View

class ViberBotApiView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'detail':'This is Viberbot api'}, status=status.HTTP_200_OK)
    def post(self, request, *args, **kwargs):
        bot_configuration = BotConfiguration(
            name='PythonSampleBot',
            avatar='',
            auth_token=VIBER_AUTH_TOKEN
        )
        viber = Api(bot_configuration)
        if request.data:
            viber_request = viber.parse_request(json.dumps(request.data))
            if isinstance(viber_request, ViberMessageRequest):
                input = request.data['message']['text']
                sender_id = viber_request.sender.id #request.data['sender']['id']
                
                viberbot_response_message(sender_id=sender_id, viber_instance=viber, prompt=input)
                
        return Response(status=status.HTTP_200_OK)