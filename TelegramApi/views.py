from django.shortcuts import render
from dotenv import load_dotenv
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .tasks import telegram_response_message
load_dotenv('.env')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')


# Create your views here.



class TelegramBotApiView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'detail':'OK'}, status=status.HTTP_200_OK)
    def post(self, request, *args, **kwargs):
        incoming_message = request.data['message']['text']
        chat_id = request.data['message']['chat']['id']
        telegram_response_message(chat_id, incoming_message)
        return Response({'detail':'OK'}, status=status.HTTP_200_OK)
