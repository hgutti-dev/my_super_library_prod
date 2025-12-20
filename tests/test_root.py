# tests/test_root.py
import pytest

pytestmark = pytest.mark.anyio


async def test_root_ok(client):
    res = await client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert "API Funcionando" in data["msg"]
