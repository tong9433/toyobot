# This Python file uses the following encoding: utf-8
from bs4 import BeautifulSoup
from selenium import webdriver
import time

class Cralwer:
    def __init__(self):
        pass

    def cralwer_offical(self):
        options = webdriver.ChromeOptions()
        options.add_argument('window-size=1920x1080')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
        options.add_argument("lang=ko_KR")

        driver = webdriver.Chrome()
        driver.implicitly_wait(5)
        driver.get('https://upbit.com/service_center/disclosure')
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
