from fastapi import Depends,APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from models.stock import Stock
import json

MONGO_DB_URL = ""

async def get_db():
    # client = AsyncIOMotorClient('localhost',27017)
    client = AsyncIOMotorClient(MONGO_DB_URL)
    db = client.get_database("daily_stock")
    return db

router = APIRouter()

# [WARN] 주말이라면 그 전주 금요일 데이터를 보여줘야 함
@router.get("/stocks/{request_date}")
async def get_daily_stocks(request_date:str, db = Depends(get_db)):
    # [TODO] request_date에 해당하는 데이터를  mongodb에서 몽땅 가져오기
    # MongoDB에서 document 읽기
    stock_collection = db.get_collection("stock")
    # result =  await stock_collection.find({"created_at":{"$eq":request_date}},{"stock_name":1}).to_list(1000)
    result =  await stock_collection.find({"created_at":{"$eq":request_date}}, projection={'_id': False}).to_list(1000)
    # result =  await stock_collection.find({"created_at":{"$gte":request_date}},{"stock_name":1}).to_list(1000)
    # print(result[3]['reference_news'])
    print(result)
    
    # [TODO] result가 빈 리스트이면 <데이터 준비중>이라는 알림을 보내야 함
    # https://fastapi.tiangolo.com/advanced/response-directly/
    return JSONResponse(content=jsonable_encoder(result))


@router.get("/stocks/ndays/{ndays}")
async def get_ndays_stocks(ndays:int, db = Depends(get_db)):

    if ndays not in(7, 30):
        # 임의 조작 시 에러 
        pass

    today = datetime.today()
    # 7주 전의 날짜 계산
    seven_days_ago = today - timedelta(days=ndays)
    # yyyy-mm-dd 형태로 포맷팅
    formatted_seven_days_ago = seven_days_ago.strftime("%Y-%m-%d")

    print(formatted_seven_days_ago)
    # [TODO] 현재 날짜부터 ndays 사이에 2회 이상 언급된 주식 정보 가져오기
    # [REF] 세부 정보는 frontend에서 처리 (이름만 뽑거나, 상세 정보를 테이블로 보여주거나 )

    result = await db.stock.aggregate([
        {"$match": {"created_at": {"$gte": formatted_seven_days_ago}}},
        {"$group": {"_id": "$stock_name", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gte": 2}}},
        {"$lookup": {
            "from": "stock",  # 같은 컬렉션을 대상으로 조회하는 경우에는 필요 없습니다. 다른 컬렉션을 대상으로 할 경우 수정 필요.
            "localField": "_id",
            "foreignField": "stock_name",
            "as": "stock_info"
        }},
        {"$project": {"_id": 0, "stock_name": "$_id", "count": 1, "stock_info": 1}}
    ]).to_list(length=None)

    print(result)


    return {"item_name": "bbang2", "item_description": "just_practice"}


@router.get("/stocks/latest")
async def get_lastest_stocks():

    # [TODO] 가장 최신 데이터 정보 제공
    return {"item_name": "bbang2", "item_description": "just_practice"}


@router.get("/stocks/oldest")
async def get_lastest_stocks():

    # [TODO] 최초의 데이터 정보 제공
    return {"item_name": "yujin", "item_description": "just_practice"}


@router.post("/stocks/create")
async def post_example_data(request_data:Stock, db = Depends(get_db)):
    print(request_data)
    # [TODO] request_date에 해당하는 데이터를 mongodb에 저장하기
    # MongoDB에서 document 읽기
    stock_collection = db.get_collection("stock")
    result =  await stock_collection.insert_one(dict(request_data))
    print(result)
    return request_data