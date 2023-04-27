from celery import Celery
import logging
import openai
import json
import requests
import os
from dotenv import load_dotenv
load_dotenv('.env')
from celery import shared_task
from viberbot.api.messages.text_message import TextMessage
# Code from here
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
openai.api_key=OPENAI_API_KEY

def response_message(chat_id, response_message_text):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
                'chat_id': chat_id,
                'text': response_message_text
                }
    response = requests.post(url, json=payload)
    print(response.json())

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
def telegram_response_message(chat_id, prompt):
    openai_response = get_openai_response(prompt)
    response_message(chat_id, openai_response)
    logging.info('RUN TASK RETURN Telegram MESSAGE DONE')

@shared_task
def viberbot_response_message(sender_id, prompt, viber_instance):
    openai_response = get_openai_response(prompt)
    viber_response_text = TextMessage(text=openai_response)
    viber_instance.send_messages(to=sender_id, messages=[viber_response_text,])
    logging.info('RUN TASK RESPONSE Viber DONE')
