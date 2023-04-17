from celery import Celery
import logging
import openai
import json
import requests
import os
from dotenv import load_dotenv
load_dotenv('.env')
from celery import shared_task
PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')
PAGE_BOT_ID = os.environ.get('PAGE_BOT_ID')
FB_WEBHOOK_VERSION = os.environ.get('FB_WEBHOOK_VERSION')
WEBHOOK_VERIFY_TOKEN = os.environ.get("WEBHOOK_VERIFY_TOKEN")
app = Celery('core', broker='redis://localhost:6379/1')
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


@shared_task
def response_message(fbid, prompt):
    openai_response = get_openai_response(prompt)
    post_facebook_message(fbid, openai_response)
    logging.info('RUN TASK RETURN FB MESSAGE DONE')

