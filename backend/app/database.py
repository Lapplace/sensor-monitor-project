import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "sensor_monitor")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# Collection lưu từng bản ghi dữ liệu upload lên (mỗi file JSON = 1 document)
readings_collection = db["readings"]


async def ensure_indexes():
    """Tạo index để truy vấn theo thời gian / site / serial cho nhanh."""
    await readings_collection.create_index([("serial", 1), ("ts", 1)])
    await readings_collection.create_index([("site", 1), ("ts", 1)])
    await readings_collection.create_index("ts")
