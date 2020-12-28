import sys
import time
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

class Sellchat:
    def __init__(self):
        self.flag = 0
        self.prc = []
        self.token = "1439118580:AAFNlBQTcu4d55z-Y1kOuGeOBSfOkbi0i4A"
        self.id = 633201480
        self.bot = telepot.Bot(self.token)

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        self.bot.sendMessage(self.id, 'ok, selling ')
        self.flag = 1
        self.prc = [ float(msg['text'].split()[0])*0.01 , float(msg['text'].split()[1])*0.01 ]

    def on_callback_query(self,msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        if query_data=='self_select':
            self.bot.sendMessage(self.id, '\'상승률 금액percent\' 입력 ')
        elif query_data == 'no':
            self.bot.sendMessage(self.id, '자동 매도 거부, tracking 시작합니다.')
            self.flag = 1
            self.prc = [False,'Null']
        else:
            self.bot.sendMessage(self.id, '지정 매도로 tracking 시작합니다.')
            self.flag = 1
            self.prc = [False, float(query_data)]


    def selling_msg(self):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='50%상승 전액', callback_data='0.5', callback_query=self.on_callback_query)],
            [InlineKeyboardButton(text='70%상승 전액', callback_data='0.7',  callback_query=self.on_callback_query)],
            [InlineKeyboardButton(text='100% 상승 전액', callback_data='1',  callback_query=self.on_callback_query)],
            [InlineKeyboardButton(text='자동매도 안함', callback_data='no',  callback_query=self.on_callback_query)],
            [InlineKeyboardButton(text='직접 입력', callback_data='self_select',  callback_query=self.on_callback_query)]
        ])
        self.bot.sendMessage(self.id, 'tracking check', reply_markup=keyboard)
        MessageLoop(self.bot, {'chat': self.on_chat_message, 'callback_query': self.on_callback_query}).run_as_thread()
        print('Listening ...')
        num = 0
        while True:
            num += 1
            if num > 90:
               self.bot.sendMessage(self.id, '초기 지정 매도로 tracking 시작합니다.')
               return (False,0.5)
            if self.flag == 0 :
               time.sleep(1)
            else:
                return self.prc
