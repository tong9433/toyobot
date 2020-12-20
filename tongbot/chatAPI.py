import os
import json
import requests
import telegram

class chatAPI:
    def __init__(self):
        self.kakao_token = "ILxGW9eys7NZm6yVoZKCYEXAZf8BvCE05nzHugo9dRoAAAF2Wig7gQ"
        self.telegram_token = "1439118580:AAFNlBQTcu4d55z-Y1kOuGeOBSfOkbi0i4A"

    def send_to_me_kakao_message(self, text):
        header = {"Authorization": 'Bearer ' + self.kakao_token}
        url = "https://kapi.kakao.com/v2/api/talk/memo/default/send" #나에게 보내기 주소
        post = {
            "object_type": "text",
            "text": text,
            "link": {
                "web_url": "https://developers.kakao.com",
                "mobile_web_url": "https://developers.kakao.com"
            },
            "button_title": "바로 확인"
        }
        data = {"template_object": json.dumps(post)}
        return requests.post(url, headers=header, data=data)

    def send_to_me_telegram_message(self, text):
        bot = telegram.Bot(token = self.telegram_token)
        bot.sendMessage(chat_id = "633201480", text=text)
        return "텔레그램 메세지 발송"



