# /app/models/__init__.py

# motor - MongoDB 용 비동기 python 라이브러리
from motor.motor_asyncio import AsyncIOMotorClient


class MongoDB:
    def __init__(self):
        self.client = None

    def connect(self):
        self.client = AsyncIOMotorClient(MONGO_DB_URL)
        print("DB 와 연결되었습니다.")
    
    def close(self):
        self.client.close()
