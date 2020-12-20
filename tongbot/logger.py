# This Python file uses the following encoding: utf-8
import sys
import logging
import datetime


class Logger:
    def __init__(self, window):
        self.window = window
        now = datetime.datetime.now().timestamp()
        time = datetime.datetime.fromtimestamp(int(now)).strftime('%Y_%m_%d_%H_%M_%S')
        self.file_name = "log/"+time + ".txt"

    def print_log(self, text):
        now = datetime.datetime.now().timestamp()
        time = datetime.datetime.fromtimestamp(int(now)).strftime('%Y-%m-%d %H:%M:%S')
        log = "[{}] {}".format(time, text)
        self.window.text_edit_bot_log.append(log)
        self.f = open(self.file_name, "a")
        self.f.write(log + "\n")
        self.f.close()
        return log
