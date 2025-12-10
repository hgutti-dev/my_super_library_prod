import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient 


load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

_client: AsyncIOMotorClient | None = None

async def get_client() -> AsyncIOMotorClient: 

    global _client 

    if _client is None: 
        _client = AsyncIOMotorClient(MONGO_URI) 
    return _client 

async def get_db(): 

    client = await get_client() 

    yield client[DB_NAME]