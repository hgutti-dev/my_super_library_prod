import pytest

pytestmark = pytest.mark.anyio

async def test_list_users_empty(client):
    res = await client.get("/books")
    assert res.status_code == 200
    assert res.json() == []