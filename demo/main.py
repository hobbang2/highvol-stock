import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

def target_date()->str:
    """대상이 되는 날짜를 반환
    [TODO] 웹 스크랩을 몇 시에 할지 먼저 정해야 함
    해당 시간 이전에 요청이 들어오면 하루 전 날짜 전달
    해당 시간 이후에 요청이 들어오면 현재 날짜 전달

    Returns:
        str: yyyy-mm-dd 형태의 날짜
    """

    # 00 ~ 21 : data prepare - yesterday
    # 21 ~    : today
    yesterday = datetime.now() - timedelta(days=1)
    # yyyy-mm-dd 형태로 포맷팅
    ret_date =  yesterday.strftime("%Y-%m-%d")
    return ret_date

# Function to make a request
def make_request():
    
    request_date = target_date()
    url = f"{BACKEND_URL}:{BACKEND_PORT}/{URL_STOCK}/{request_date}"  # Replace with your API endpoint
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
         
    else:
        return None


# Streamlit UI
st.title(f"Stock Information {target_date()}")
st.caption("저녁 9시에 당일 날짜 데이터로 업데이트")

stock_data = make_request()
df = pd.DataFrame(stock_data)[['sosok','stock_name','reference_news', 'trade_volume', 'increase_rate','day_change_proportion','stock_price','created_at']]
df['reference_news'] = df['reference_news'].apply(lambda x: x[:3])
df['reference_news'] = df['reference_news'].apply(lambda x: '<br><br>'.join([f'<a href={item["link"]}>{item["title"]}</a>' for item in x]))
df_html = df.to_html(escape=False)

large_trade_volume_stock = df[(df['trade_volume'] > 10000000)&(df['sosok'] == 0)]['stock_name'].to_list()
precious_stock = df[(df['trade_volume'] > 10000000)&(df['increase_rate'] > 29)&(df['sosok'] == 0)]['stock_name'].to_list()


md = st.text_area('KOSPI - 천만 거래량',
                  ', '.join(large_trade_volume_stock))


md = st.text_area('KOSPI - 천만 거래량',
                  ', '.join(precious_stock))

large_trade_volume_stock = df[(df['trade_volume'] > 10000000)&(df['sosok'] == 1)]['stock_name'].to_list()
precious_stock = df[(df['trade_volume'] > 10000000)&(df['increase_rate'] > 29)&(df['sosok'] == 1)]['stock_name'].to_list()


md = st.text_area('KOSDAQ - 천만 거래량',
                  ', '.join(large_trade_volume_stock))


md = st.text_area('KOSDAQ - 상한가 + 천만 거래량',
                  ', '.join(precious_stock))

st.write(df_html, unsafe_allow_html=True)
# st.dataframe(df)  # Same as st.write(df)