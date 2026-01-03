import pytest

pytestmark = pytest.mark.anyio

def sample_payload(**overrides):
    """
    Payload base EXACTO para BookCreate (según src/schemas/book.py).
    """
    payload = {
        "first_name": "Testing User",
        "last_name": "Test lastname",
        "email": "just_test@test.com",
        "password": "123456789",
        "role" : "user"
    }
    payload.update(overrides)
    return payload

async def test_list_users_empty(client):
    res = await client.get("/users")
    assert res.status_code == 200
    assert res.json() == {"message": "Get All - Users"}

async def test_create_user_returns_userread(client):
    res = await client.post("/users", json=sample_payload())
    assert res.status_code == 201, res.text

    data = res.json()

    # UserRead: id + campos base (sin password)
    assert "id" in data and isinstance(data["id"], str) and data["id"]
    assert data["first_name"] == "Testing User"
    assert data["last_name"] == "Test lastname"
    assert data["email"] == "just_test@test.com"
    assert data["role"] == "user"

    # Seguridad: no debe devolver password (ni hash)
    assert "password" not in data
    assert "hashed_password" not in data
