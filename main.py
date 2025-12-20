from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.db.db import get_client, DB_NAME
from src.routes import book_routes as books_rts

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    client = await get_client()
    app.state.client = client
    app.state.db = client[DB_NAME]
    # Si necesitas inicializar índices, colas, etc., hazlo aquí
    yield
    # --- Shutdown ---
    # Cierra recursos aquí si aplica (ej., cerrar cliente de DB)
    # await app.state.client.close()  # depende de tu driver; ajusta según tu implementación

app = FastAPI(
    title="My Super Library - Production enviroment",
    lifespan=lifespan,
)

# Registra rutas
app.include_router(books_rts.router)

@app.get("/")
async def root():
    return {"ok": True, "msg": "API Funcionando!"}

