# tests/test_root.py
import pytest

""" 
¿Qué hace esto?

Aplica automáticamente el marcador @pytest.mark.anyio a todo el archivo.

Le dice a pytest que:

Este archivo contiene tests async

Debe ejecutarlos usando AnyIO, que permite usar asyncio correctamente

👉 Gracias a esto no necesitas decorar cada test async individualmente.
"""
pytestmark = pytest.mark.anyio


""" 
🔹 ¿Qué es esto?

Es un test asíncrono

client es un fixture (definido en conftest.py)

Normalmente es un httpx.AsyncClient

Está conectado directamente a tu app FastAPI (ASGI)

No levanta un servidor real

👉 Esto es testing rápido y aislado, ideal para CI.
"""
async def test_root_ok(client):
    res = await client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert "Welcome to My Super Library API :)!!" in data["msg"]
