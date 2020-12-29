import os
import json
import requests
import telegram

class chatAPI:
    def __init__(self, window):
        self.telegram_token = window.telegram_token
        self.telegram_id = window.telegram_id

    def send_to_me_telegram_message(self, text):
        bot = telegram.Bot(token = self.telegram_token)
        bot.sendMessage(chat_id = self.telegram_id, text=text)
