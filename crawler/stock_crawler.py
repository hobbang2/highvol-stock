from motor.motor_asyncio import AsyncIOMotorClient
from agents.news_agent import lookup as news_agent
from selenium.webdriver.common.by import By 
from datetime import datetime, timedelta, timezone
import chromedriver_autoinstaller as ca
from selenium import webdriver
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import time, os, sys, re
from typing import List
import urllib.request
import asyncio
import json

load_dotenv()
MONGO_DB_URL = os.environ.get('MONGO_DB_URL')

URL_RISE = "https://finance.naver.com/sise/sise_rise.naver?sosok="
URL_FALL = "https://finance.naver.com/sise/sise_fall.naver?sosok="
# 상한가 종목을 따로 파싱하지 않고 상승률이 29% 초과면 상한가로 보자
URL_UPPER = "https://finance.naver.com/sise/sise_upper.naver"
LABEL = ["현재가", "전일비", "등락률", "거래량"]
LABEL = {"현재가": "stock_price", 
            "전일비": "day_change_proportion",
            "등락률": "increase_rate",
            "거래량": "trade_volume"}

# 10개의 기사를 관련도 순으로 전달
NAVER_NEWS_URL = os.environ.get('NAVER_NEWS_URL')
NAVER_CLIENT_ID = os.environ.get('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.environ.get('NAVER_CLIENT_SECRET')

LOWER_BOUND_TRADE_AMOUNT = 10000000
LOWER_BOUNT_INCREASE_RATE = 29.0

# 상승 목록 가져오기 
# - 종목명, 현재가, 전일비, 등락률, 거래량 

def ts(sleep_sec:int) : 
    
    time.sleep(ts)
    
def is_recent_news(target_date:str, today_date, diff_day:int=7):

    # 주어진 문자열을 datetime 객체로 변환
    given_date = datetime.strptime(target_date, '%a, %d %b %Y %H:%M:%S %z')
    # 날짜 차이 계산
    date_difference = today_date - given_date
    # 날짜 차이가 기준일자 보다 적게 나는지 여부 반환
    return 0 <= date_difference.days <= diff_day

def get_input_str_for_summary(reference_news:List[dict]):

    title_str ='\n'.join( [f"- {item['title']}" for item in reference_news])
    ret_str = f"""
    header:
    {title_str}
    answer:
    """
    return ret_str

# 기본 반환 결과 개수: 10개
def get_news_information(stock_name:str, sort = "sim")->list:

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
    cur_URL = NAVER_NEWS_URL.format(query=encText, sort=sort)

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

def get_stock_information(URL:str, sosok:int)->list:
    
    """주식 정보를 크롤링하는 함수

    Args:
        sosok (int): 0이면 코스피, 1이면 코스닥

    Returns:
        list: 종목명, 현재가, 전일비, 등락률, 거래랑이 dictionary로 포함된 list
    """
    # Linux 환경에서 chromdriver를 찾지 못하는 문제로 인해 추가
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)
    # driver = webdriver.Chrome()

    time.sleep(2); driver.get(f'{URL}{sosok}')
    main = driver.window_handles
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    header_list = soup.find('table', class_="type_2").find_all('th')

    header_list = [item.get_text() for item in header_list]
    header_dict = { idx:LABEL[item] for idx, item in enumerate(header_list) if item in LABEL}

    stock_info_list = soup.find('table', class_="type_2").find_all('tr')[2:]
    result = []

    # UTC+09:00의 timezone 객체 생성
    utc_offset = timedelta(hours=9)
    timezone_utc_9 = timezone(utc_offset)
    # UTC+09:00의 현재 시간
    current_time_utc_9 = datetime.now(timezone_utc_9)

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

        reference_information['increase_rate'] = float(reference_information['increase_rate'].strip('%'))

        # 수집 기준을 만족하지 못하면 수집하지 않음 
        if((reference_information['trade_volume'] < LOWER_BOUND_TRADE_AMOUNT)
        and ( reference_information['increase_rate'] < LOWER_BOUNT_INCREASE_RATE) ):
            continue

        reference_information["stock_name"] = stock_name
        reference_information["stock_code"] = stock_code
        # 아래 두 가지 작업은 크롤링 후에 각 item의 stock_name만 가지고 진행해도 됨
        # 네이버 뉴스 API를 활용하여 관련 뉴스 정보를 가져옴f'"{stock_name}"'
        news_info_list = get_news_information(f'특징주+"{stock_name}" -상한가보드 -상한가종목',"date")
        news_info_list += get_news_information(f'+{stock_name} -상한가보드 -상한가종목',"sim")
        news_info_list += get_news_information(f'+"{stock_name}" -상한가보드 -상한가종목',"date")

        # 뉴스 정보를 최신순으로 정렬
        for item in news_info_list:
            item['refinePubDate'] = datetime.strptime(item['pubDate'], '%a, %d %b %Y %H:%M:%S %z').strftime("%Y-%m-%d")

        reference_information["reference_news"] = sorted(news_info_list, key=lambda item: item['refinePubDate'], reverse = True) 
        # 수집된 뉴스 정보 중 오늘 날짜로부터 일주일 이내의 것만 수집
        pass_news_info = [ item for item in reference_information["reference_news"] if is_recent_news(item['pubDate'], current_time_utc_9)][:10]

        # gpt로 뉴스 타이틀을 활용하여 상승 요인 추출
        target_mode = "falls" if reference_information['increase_rate'] < 0 else "rises"
        reference_information["summary"] = f"기준일자부터 일주일 간 언급된 기사가 없음" \
                                            if(0 == len(pass_news_info)) else news_agent(target_mode,\
                                                      get_input_str_for_summary(pass_news_info))
        reference_information["created_at"] = current_time_utc_9.strftime("%Y-%m-%d")
        reference_information["sosok"] = sosok

        result.append(reference_information)
    return result


async def insert_stock_info_to_db(stock_information:List[dict]):

    async def get_db():
        client = AsyncIOMotorClient(MONGO_DB_URL)
        db = client.get_database("daily_stock")
        return db

    db = await get_db()
    stock_collection = db.get_collection("stock")
    result = await stock_collection.insert_many(stock_information)

    return result

async def main():
    KOSPI_rise_info  = get_stock_information(URL_RISE, 0)
    KOSDAQ_rise_info = get_stock_information(URL_RISE,1)
    KOSPI_fall_info  = get_stock_information(URL_FALL,0)
    KOSDAQ_fall_info = get_stock_information(URL_FALL, 1)

    await insert_stock_info_to_db(KOSPI_rise_info)
    await insert_stock_info_to_db(KOSDAQ_rise_info)
    await insert_stock_info_to_db(KOSPI_fall_info)
    await insert_stock_info_to_db(KOSDAQ_fall_info)

if __name__ == "__main__":
    asyncio.run(main())

