import sys
import time
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

class Sellchat:
    def __init__(self, window, parent):
        self.window = window
        self.parent = parent
        self.flag = 0
        self.telegram_token = window.telegram_token
        self.telegram_id = window.telegram_id
        self.bot = telepot.Bot(self.telegram_token)

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        self.bot.sendMessage(self.telegram_id, 'ok, selling ')
        self.parent.sell_status = [ float(msg['text'].split()[0])*0.01 , float(msg['text'].split()[1])*0.01 ]

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        if query_data == 'no':
            self.bot.sendMessage(self.telegram_id, '자동 매도 거부, tracking 시작합니다.')
            self.parent.sell_status = [False, None]

    def selling_msg(self):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='자동매도 안함', callback_data='no',  callback_query=self.on_callback_query)]
        ])
        self.bot.sendMessage(self.telegram_id, 'tracking check', reply_markup=keyboard)
        MessageLoop(self.bot, {'chat': self.on_chat_message, 'callback_query': self.on_callback_query}).run_as_thread()
