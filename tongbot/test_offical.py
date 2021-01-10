import requests
import re
from pyupbit import Upbit
import pyupbit
from tqdm import tqdm
from openpyxl import Workbook

def day_calc(anno_time, time_set):
    cr_time = anno_time.split('T')
    year = cr_time[0].split('-')
    time = cr_time[1].split('+')[0].split(':')

    if int(time[0]) - 9 < 0:
        if int(year[2]) - 1 != 0:
            year[2] = int(year[2]) - 1
        else:
            if int(year[1]) - 1 != 0:
                year[2] = month_range(year[0], int(year[1]) - 1)
                year[1] = int(year[1]) - 1
            else:
                year[0] = int(year[0]) - 1
                year[1] = '12'
                year[2] = '31'

    time[0] = (int(time[0]) + 15) % 24
    ##  시간을 추가했는데, 24시가 넘었을때,
    if int(time[0])+time_set >= 24:
        ## 일을 올려줘야되는데 일이 올라감에 따라 월도 달라질때 1/31일 경우
        if int(year[2])+1 > month_range(year[0], year[1]):
            ## 월도 달라지는데 그 월이 12월일 경우.
            if int(year[1])+1 > 12:
                year[0] = int(year[0]) + 1
                year[1] = '01'
                year[2] = '01'
            ## 12월이 아닌경우
            else:
                year[1] = int(year[1])+1
                year[2] = '01'
        ## 일만 올라갈 경우
        else:
            year[2] = int(year[2]) + 1
        time[0] = int(time[0]) - 23

    else:
        time[0] = int(time[0])+1

    ##  2021-01-01 12:37:00

    for idx, ent in enumerate(year):
        year[idx] = str(year[idx])
    for idx, ent in enumerate(time):
        time[idx] = str(time[idx])

    if len(time[0]) == 1:
        time[0] = '0' + time[0]
    if len(year[1]) == 1:
        year[1] = '0' + year[1]
    if len(year[2]) == 1:
        year[2] = '0' + year[2]

    return str('-'.join(year) + ' ' + ':'.join(time))

def month_range(year, month):
    ins_year = 1
    ins_month = 1
    ins_now_month = 0
    while True:
        now_month = 31
        if ins_month == 4 or ins_month == 6 or ins_month == 9 or ins_month == 11:
            now_month = 30
        elif ins_month == 2:
            if (ins_year % 4 == 0 and ins_year % 100 != 0) or ins_year % 400 == 0:
                now_month = 29
            else:
                now_month = 28
        if ins_year == year and ins_month == month:
            break
        ins_now_month += now_month
        ins_month += 1
        if ins_month > 12:
            ins_month = 1
            ins_year += 1

    return now_month

def api_call(market_name, base_time, count):
    url = "https://api.upbit.com/v1/candles/minutes/1"
    querystring = {"market": market_name,
                   "count": count,
                   "to":base_time,
                   "unit":"1"}
    response = requests.request("GET", url, params=querystring)
    return response.json()

def excel_write(total_arr):
    write_wb = Workbook()
    write_ws = write_wb.active
    for i in total_arr:
        write_ws.append(i)
    write_wb.save('data_analysis.xlsx')


if __name__ == "__main__":
    only_coin_name = re.compile('[^ a-zA-Z]')
    krw_list = pyupbit.get_tickers(fiat="KRW")
    btc_list = pyupbit.get_tickers(fiat="BTC")
    krw_dict = {string: 0 for string in krw_list}
    btc_dict = {string: 0 for string in btc_list}
    time_set = 1
    total_arr = []
    for idx in tqdm(range(1,72)):
        url = "https://api-manager.upbit.com/api/v1/notices?page="+str(idx)+"&per_page=20&thread_name=general"
        res = requests.request("GET", url)
        upbit_announcement = res.json()["data"]["list"]
        for idx, unit in enumerate(upbit_announcement):
            result = only_coin_name.sub('', unit['title'])
            coin_name_list = result.split()
            for coin in coin_name_list:
                flag = 0
                try:
                    if coin == 'BTC':
                        continue
                    if 'KRW-'+str(coin) in krw_dict:
                        an_time = day_calc(unit['created_at'], 0)
                        temp_list = api_call('KRW-' + str(coin), an_time, 1)
                        announce_price = temp_list[0]['trade_price']

                        an_time = day_calc(unit['created_at'],time_set)
                        temp_list = api_call('KRW-'+str(coin), an_time, 60)
                        max_price = 0
                        for time_list in temp_list:
                            cur_price = time_list['trade_price']
                            if announce_price * 1.5 < cur_price and max_price < cur_price :
                                max_price = cur_price

                        if max_price != 0:
                            temp_arr = []
                            temp_arr.append(unit['title'])
                            temp_arr.append('KRW-'+str(coin))
                            temp_arr.append(announce_price)
                            temp_arr.append(max_price)
                            temp_arr.append(max_price*100/announce_price)
                            temp_arr.append(unit['created_at'])
                            total_arr.append(temp_arr)

                    if 'BTC-'+str(coin) in btc_dict:
                        an_time = day_calc(unit['created_at'], 0)
                        temp_list = api_call('BTC-'+str(coin), an_time, 1)
                        announce_price = temp_list[0]['trade_price']

                        an_time = day_calc(unit['created_at'], time_set)
                        temp_list = api_call('BTC-' + str(coin), an_time, 60)
                        max_price = 0
                        for time_list in temp_list:
                            cur_price = time_list['trade_price']
                            if announce_price * 1.5 < cur_price and max_price < cur_price :
                                max_price = cur_price

                        if max_price != 0:
                            temp_arr = []
                            temp_arr.append(unit['title'])
                            temp_arr.append('KRW-' + str(coin))
                            temp_arr.append(announce_price)
                            temp_arr.append(max_price)
                            temp_arr.append(max_price * 100 / announce_price)
                            temp_arr.append(unit['created_at'])
                            total_arr.append(temp_arr)
                except Exception as e:
                    continue
                    print(type(e))
                    print(coin)
                    print(unit['title'])
                    input()



    excel_write(total_arr)

