from fastapi import Depends,APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from models.stock import Stock
from dotenv import load_dotenv
import json
import os


# 현재 파일의 경로를 가져오기
current_dir = os.path.dirname(os.path.realpath(__file__))
# 부모 디렉토리로 이동
parent_dir = os.path.join(current_dir, os.pardir)
# .env 파일 로드
env_path = os.path.join(parent_dir, '.env')
load_dotenv(dotenv_path=env_path)

MONGO_DB_URL = os.getenv("MONGODB_URL")

async def get_db():
    
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


@router.get("/stocks/historical/{nweeks}")
async def get_nweeks_stocks(nweeks:int, db = Depends(get_db)):
    # if nweeks not in(4, 30):
        # 임의 조작 시 에러 
        # return JSONResponse(content={"error": "Invalid number of weeks. Must be 7 or 30."}, status_code=400)
    today = datetime.today()
    # nweeks 전의 날짜 계산
    nweeks_ago = today - timedelta(weeks=nweeks)
    # yyyy-mm-dd 형태로 포맷팅
    formatted_nweeks_ago = nweeks_ago.strftime("%Y-%m-%d")

    #  현재 날짜부터 ndays 사이에 2회 이상 언급된 주식 정보 가져오기
    result = await db.stock.aggregate([
        {"$match": {"created_at": {"$gte": formatted_nweeks_ago}}},
        {"$group": {"_id": {"stock_name": "$stock_name", "stock_code": "$stock_code"}, "count": {"$sum": 1}}},
        {"$match": {"count": {"$gte": 2}}},
        {"$lookup": {
            "from": "stock",  # 같은 컬렉션을 대상으로 조회하는 경우에는 필요 없습니다. 다른 컬렉션을 대상으로 할 경우 수정 필요.
            "localField":  "_id.stock_code",
            "foreignField": "stock_code",
            "as": "stock_info"
        }},
        {"$project": {
            "_id": False,
            "stock_name": "$_id.stock_name",
            "stock_code": "$_id.stock_code",
            "created_at": "$stock_info.created_at",
            "stock_price": "$stock_info.stock_price",
            "count": 1}
        },
        {"$sort": {"count": -1}
         }
    ]).to_list(length=None)

    print(result)

    return JSONResponse(content=jsonable_encoder(result))


@router.get("/stocks/latest")
async def get_lastest_stocks():

    # [TODO] 가장 최신 데이터 정보 제공
    return {"item_name": "bbang", "item_description": "just_practice"}


@router.get("/stocks/oldest")
async def get_lastest_stocks():

    # [TODO] 최초의 데이터 정보 제공
    return {"item_name": "bbang", "item_description": "just_practice"}


@router.post("/stocks/create")
async def post_example_data(request_data:Stock, db = Depends(get_db)):
    print(request_data)
    # [TODO] request_date에 해당하는 데이터를 mongodb에 저장하기
    # MongoDB에서 document 읽기
    stock_collection = db.get_collection("stock")
    result =  await stock_collection.insert_one(dict(request_data))
    print(result)
    return request_data


@router.get("/stocks/update/{from_dt}/{to_dt}")
async def post_example_data(from_dt:str, to_dt:str, db = Depends(get_db)):
    # 업데이트할 데이터의 조건
    filter_condition = {"created_at": from_dt}
    # 업데이트할 내용
    update_data = {"$set": {"created_at": to_dt}}  # 새로운 날짜로 업데이트

    stock_collection = db.get_collection("stock")

    # MongoDB에서 업데이트 실행
    result = stock_collection.update_many(filter_condition, update_data)

    print(result)
    # 업데이트된 문서의 개수 확인
    if result:
        return {"message": f" documents updated successfully."}
    else:
        raise HTTPException(status_code=404, detail="No documents found for the given condition.")