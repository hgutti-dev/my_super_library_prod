from fastapi import FastAPI
from src.db.db import get_client, DB_NAME


app = FastAPI(title="My Super Library - Production enviroment")

@app.on_event("startup") 
async def _startup():
    client = await get_client() 

    db = client[DB_NAME]


@app.get("/")
async def root():
    return {"ok": True, "msg" : "API Funcionando!"}