import os
from datetime import datetime

from flask import Flask, abort, request
import requests
from bs4 import BeautifulSoup
from urllib.request import urlretrieve

# https://github.com/line/line-bot-sdk-python
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET"))


def movie():
    target_url = 'https://movies.yahoo.com.tw/'
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    content = ""
    for index, data in enumerate(soup.select('div.movielist_info h1 a')):
        if index == 20:
            return content
        title = data.text
        link = data['href']
        content += '{}\n{}\n'.format(title, link)
    return content


@app.route("/", methods=["GET", "POST"])
def callback():
    if request.method == "GET":
        return "Hello Heroku"
    if request.method == "POST":
        signature = request.headers["X-Line-Signature"]
        body = request.get_data(as_text=True)

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            abort(400)

        return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    get_message = event.message.text
    if get_message == "最新電影":
        a = movie()
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=a))
    # Send To Line
    else:
        reply = TextSendMessage(text=f"{get_message}")
        line_bot_api.reply_message(event.reply_token, reply)
