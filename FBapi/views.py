from django.shortcuts import render
from django.views import generic
from django.http.response import HttpResponse
import json
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import requests
import os
from dotenv import load_dotenv
import openai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .tasks import response_message
from datetime import datetime
load_dotenv('.env')

PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')
PAGE_BOT_ID = os.environ.get('PAGE_BOT_ID')
FB_WEBHOOK_VERSION = os.environ.get('FB_WEBHOOK_VERSION')
WEBHOOK_VERIFY_TOKEN = os.environ.get("WEBHOOK_VERIFY_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key=OPENAI_API_KEY

def post_facebook_message(fbid, response_message):
    post_message_url = f'https://graph.facebook.com/{FB_WEBHOOK_VERSION}/me/messages?access_token={PAGE_ACCESS_TOKEN}'
    response_msg = json.dumps({
                                "sender":{"id":PAGE_BOT_ID},
                                "recipient":{"id":fbid}, 
                                "message":{"text":response_message}
                                })
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)

class MessengerView(generic.View):
    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == WEBHOOK_VERIFY_TOKEN:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                if 'message' in message:   
                    print("START SENDING ANSWER")
                    post_facebook_message(message['sender']['id'], message['message']['text'])  
                    print("END SENDING ANSWER PROCESS")
        return HttpResponse()
    
# FB page with APIView and OpenAI response
def get_openai_response(prompt, model='gpt-3.5-turbo',max_tokens=1000, temperature=0):
        response = openai.ChatCompletion.create(
            model=model,
            messages = [
                {"role":"user","content":prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        print("OPENAI RESPONSE", response['choices'][0]['message'].get('content', ''))
        return response['choices'][0]['message'].get('content', '')

class PageMessageViewV2(APIView):
    def get(self, request, *args, **kwargs):
        if request.query_params.get('hub.verify_token') == WEBHOOK_VERIFY_TOKEN:
            return HttpResponse(request.query_params.get("hub.challenge"))
        return Response({"Error":"Invalid Token"}, status = status.HTTP_400_BAD_REQUEST)
    def post(self, request, *args, **kwargs):
        incoming_message = request.data
        print(incoming_message)
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                message_sender_id = message['sender']['id']
                message_text = message['message']['text']
                response_message.delay(message_sender_id, message_text)
        return Response({'detail':'Ok'}, status=status.HTTP_200_OK)
