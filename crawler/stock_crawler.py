from selenium import webdriver
import chromedriver_autoinstaller as ca
from selenium.webdriver.common.by import By 
import time, os, sys
from bs4 import BeautifulSoup
import re
import os
import sys
import urllib.request
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import json
import asyncio



lower_bound_trade_amount = 10000000

# 상승 목록 가져오기 
# - 종목명, 현재가, 전일비, 등락률, 거래량 


def ts(sleep_sec:int) : 
    
    time.sleep(ts)


def get_news_information(stock_name:str)->list:

    """
    return data example:
     "items":[
                {
                        "title":"<b>현대무벡스<\/b>, 급락 하루만에 10% 급등…3500원선 재돌파",
                        "originallink":"http:\/\/www.econonews.co.kr\/news\/articleView.html?idxno=312565",
                        "link":"http:\/\/www.econonews.co.kr\/news\/articleView.html?idxno=312565",
                        "description":"<b>현대무벡스<\/b>가 급등 중이다. ...",
                        "pubDate":"Mon, 13 Nov 2023 10:20:00 +0900"
                },
    """

    encText = urllib.parse.quote(stock_name)
    cur_URL = NAVER_NEWS_URL.format(query=encText)

    request = urllib.request.Request(cur_URL)
    request.add_header("X-Naver-Client-Id",NAVER_CLIENT_ID)
    request.add_header("X-Naver-Client-Secret",NAVER_CLIENT_SECRET)
    response = urllib.request.urlopen(request)

    rescode = response.getcode()
    if(rescode==200):
        response_body = response.read()
        return json.loads(response_body.decode('utf-8'))["items"]
    else:
        print(f"{stock_name}-Error Code:{rescode}")
        return []

def get_stock_information(sosok:int)->list:
    """주식 정보를 크롤링하는 함수

    Args:
        sosok (int): 0이면 코스피, 1이면 코스닥

    Returns:
        list: 종목명, 현재가, 전일비, 등락률, 거래랑이 dictionary로 포함된 list
    """
    driver = webdriver.Chrome(ca.install())
    time.sleep(2); driver.get(f'{URL_RISE}{sosok}')
    main = driver.window_handles
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    header_list = soup.find('table', class_="type_2").find_all('th')

    header_list = [item.get_text() for item in header_list]
    header_dict = { idx:LABEL[item] for idx, item in enumerate(header_list) if item in LABEL}

    stock_info_list = soup.find('table', class_="type_2").find_all('tr')[2:]
    result = []

    for stock_info in stock_info_list:

        stock_name_elem = stock_info.find('a', class_='tltle')

        # 구분선, 의도적인 공백이 있을 수 있음
        if( None == stock_name_elem):
            continue

        stock_name = stock_name_elem.text.strip()
        stock_code = re.search(r'code=(\d+)', stock_name_elem['href']).group(1)

        reference_information_list = stock_info.find_all('td', class_='number')

        # 'N'과 '종목명'이 빠졌으므로 index에 2를 더해줌
        reference_information = { header_dict[idx + 2] : (item.get_text().strip().replace(',','')) \
                                    for  idx, item in enumerate(reference_information_list) if idx + 2 in header_dict }
        
        reference_information['trade_volume'] = int(reference_information['trade_volume'])

        if(reference_information['trade_volume'] < lower_bound_trade_amount):
            continue

        reference_information['increase_rate'] = float(reference_information['increase_rate'].strip('%'))

        reference_information["stock_name"] = stock_name
        reference_information["stock_code"] = stock_code
        # 아래 두 가지 작업은 크롤링 후에 각 item의 stock_name만 가지고 진행해도 됨
        # 네이버 뉴스 API를 활용하여 관련 뉴스 정보를 가져옴
        reference_information["reference_news"] = get_news_information(stock_name)
        # [TODO] gpt로 뉴스 정보를 요약한 정보를 가져옴
        reference_information["summary"] = ""
        reference_information["created_at"] = datetime.now().strftime("%Y-%m-%d")
        reference_information["sosok"] = sosok

        result.append(reference_information)
    return result


async def insert_stock_info_to_db(stock_information:List[dict]):

    async def get_db():
        # client = AsyncIOMotorClient('localhost',27017)
        client = AsyncIOMotorClient(MONGO_DB_URL)
        db = client.get_database("daily_stock")
        return db

    db = await get_db()
    stock_collection = db.get_collection("stock")
    result =  await stock_collection.insert_many(stock_information)

    return result

async def main():
    KOSPI_rise_info  = get_stock_information(0)
    KOSDAQ_rise_info = get_stock_information(1)

    await insert_stock_info_to_db(KOSPI_rise_info)
    await insert_stock_info_to_db(KOSDAQ_rise_info)

if __name__ == "__main__":
    asyncio.run(main())

