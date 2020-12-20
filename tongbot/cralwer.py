# This Python file uses the following encoding: utf-8
from bs4 import BeautifulSoup
import requests


class Cralwer:
    def __init__(self):
        pass

    def cralwer_notice(self):
        webpage = requests.get("https://upbit.com/service_center/notice")
        soup = BeautifulSoup(webpage.content, "html.parser")
        print(soup)
