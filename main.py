import os
import flask
import re
import requests as REQ
from flask import request

from truecallerpy import search_phonenumber


APP = flask.Flask(__name__)
TGURL = f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/sendMessage"

pattern = r'^\d{10}$'

id = os.getenv('API_KEY')

@APP.route('/')
def home():
    return "It works 🙂"

@APP.route('/getinfo/', methods=['GET', 'POST'])
def index():
    msg = ''
    body = request.get_json()

    name = body['message']['from']['first_name']
    chat_id = body['message']['from']['id']
    chat_txt = body['message']['text']

    if chat_txt == "/start":
        msg = f"Hi, {name} \nWelcome to Telegram Truecaller Bot"
    else:
        try:
            number = int(chat_txt)
            res = search_phonenumber(str(number), "IN", id)
            data = res.get('data', [])
            if data:
                info = data[0]
                name = info.get('name', 'MR. Unknown')
                image = info.get('image', None)
                carrier = info['phones'][0].get('carrier', None)
                city = info['addresses'][0].get('city', 'None')

                internet_addresses = info.get('internetAddresses', [])
                internet_address_id = internet_addresses[0].get(
                    'id', None) if internet_addresses else None

                msg = f"Name : {name}\nCarrier : {carrier}\nEmail : {internet_address_id}\nCity : {city}\n\nPhoto : {image}"
            else:
                msg = "No data found for the provided phone number."
        except ValueError:
            msg = "Error: Please enter a valid 10-digit phone number."

    params = {
        'chat_id': chat_id,
        'text': msg,
        'parse_mode': 'HTML'
    }
    r = REQ.post(url=TGURL, params=params)

    if r.ok:
        return 'Message sent successfully<br>' + r.text
    else:
        return 'Failed to send message'+r.text
