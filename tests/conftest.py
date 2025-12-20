""" 
Descripcion de funcion de archivo:  Base de testing lista para crecer

tests/conftest.py con:

un app de FastAPI importado desde tu proyecto

un AsyncClient de httpx para pegarle a tus endpoints sin levantar servidor

overrides de dependencias (ej: DB o repositorios) para que NO toque Mongo real
"""

# tests/conftest.py
import os
import pytest
from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from main import app
from src.db import db as db_module  # para overridear get_db


@pytest.fixture(scope="session")
def anyio_backend():
    # Necesario para que pytest soporte async correctamente
    return "asyncio"


@pytest.fixture(scope="session")
def test_mongo_uri():
    # En CI lo pondremos como env var (mongo service).
    # Localmente tú puedes ponerlo en tu .env o exportarlo.
    uri = os.getenv("MONGO_URI_TEST") or os.getenv("MONGO_URI")
    if not uri:
        raise RuntimeError(
            "No se encontró MONGO_URI_TEST ni MONGO_URI. "
            "Define MONGO_URI_TEST para ejecutar tests."
        )
    return uri


@pytest.fixture(scope="session")
def test_db_name():
    return os.getenv("DB_NAME_TEST", "my_super_library_test")


@pytest.fixture(scope="session")
async def mongo_client(test_mongo_uri):
    client = AsyncIOMotorClient(test_mongo_uri)
    yield client
    client.close()


@pytest.fixture(scope="function")
async def test_db(mongo_client, test_db_name):
    db = mongo_client[test_db_name]

    # Limpieza antes de cada test (simple y efectivo)
    collections = await db.list_collection_names()
    for col in collections:
        await db[col].delete_many({})

    yield db


@pytest.fixture(scope="function")
async def client(test_db):
    async def override_get_db():
        yield test_db

    app.dependency_overrides[db_module.get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


