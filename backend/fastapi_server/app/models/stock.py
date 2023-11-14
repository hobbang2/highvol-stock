from datetime import datetime
from pydantic import BaseModel
from typing import List

# [TODO] 추가 여부 확인
# - 코스피, 코스닥 분류, 상한가, 천만 거래 여부
class Stock(BaseModel):
    stock_code:int
    stock_name:str
    stock_price:int
    reference_news:List[str]
    summary:str
    trade_volume:int
    day_change_proportion:int
    increase_rate:float
    created_at:str