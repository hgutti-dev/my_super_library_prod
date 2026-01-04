# tests/test_users.py
import pytest

pytestmark = pytest.mark.anyio


def sample_payload(**overrides):
    """
    Payload base EXACTO para UserCreate (según src/schemas/users.py).
    """
    payload = {
        "first_name": "Testing User",
        "last_name": "Test lastname",
        "email": "just_test@test.com",
        "password": "123456789",
        "role": "user",
    }
    payload.update(overrides)
    return payload


async def test_list_users_empty(client):
    """
    GET /users debe devolver lista vacía si no hay usuarios.
    (Tu router tiene response_model=List[UserRead])
    """
    res = await client.get("/users")
    assert res.status_code == 200, res.text
    assert res.json() == []


async def test_create_user_returns_userread(client):
    """
    POST /users debe devolver UserRead (sin password/hashed_password).
    """
    res = await client.post("/users", json=sample_payload())
    assert res.status_code == 201, res.text

    data = res.json()

    assert "id" in data and isinstance(data["id"], str) and data["id"]
    assert data["first_name"] == "Testing User"
    assert data["last_name"] == "Test lastname"
    assert data["email"] == "just_test@test.com"
    assert data["role"] == "user"

    # Seguridad: no debe devolver password (ni hash)
    assert "password" not in data
    assert "hashed_password" not in data


async def test_get_user_by_id(client):
    """
    GET /users/{user_id} debe devolver el usuario creado.
    """
    created_res = await client.post("/users", json=sample_payload(email="u1@test.com"))
    assert created_res.status_code == 201, created_res.text
    created = created_res.json()
    user_id = created["id"]

    res = await client.get(f"/users/{user_id}")
    assert res.status_code == 200, res.text
    got = res.json()

    assert got["id"] == user_id
    assert got["email"] == "u1@test.com"
    assert "password" not in got
    assert "hashed_password" not in got


async def test_list_users_with_email_filter(client):
    """
    GET /users?email=... debe filtrar por email exacto (según tu router).
    """
    await client.post("/users", json=sample_payload(email="a@test.com", first_name="A"))
    await client.post("/users", json=sample_payload(email="b@test.com", first_name="B"))

    res = await client.get("/users", params={"email": "b@test.com"})
    assert res.status_code == 200, res.text
    data = res.json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["email"] == "b@test.com"
    assert data[0]["first_name"] == "B"


async def test_get_user_by_email_route(client):
    """
    GET /users/by-email/{email} debe devolver el usuario correcto.
    """
    await client.post("/users", json=sample_payload(email="findme@test.com"))

    res = await client.get("/users/by-email/findme@test.com")
    assert res.status_code == 200, res.text
    data = res.json()

    assert data["email"] == "findme@test.com"
    assert "id" in data and data["id"]
    assert "password" not in data
    assert "hashed_password" not in data


async def test_update_user_patch(client):
    """
    PATCH /users/{user_id} debe actualizar campos permitidos por UserUpdate.
    """
    created_res = await client.post(
        "/users",
        json=sample_payload(email="patch@test.com", first_name="Old", last_name="Name"),
    )
    assert created_res.status_code == 201, created_res.text
    user_id = created_res.json()["id"]

    patch_res = await client.patch(
        f"/users/{user_id}",
        json={"first_name": "New", "role": "admin"},
    )
    assert patch_res.status_code == 200, patch_res.text
    updated = patch_res.json()

    assert updated["id"] == user_id
    assert updated["first_name"] == "New"
    assert updated["role"] == "admin"
    assert updated["email"] == "patch@test.com"
    assert "password" not in updated
    assert "hashed_password" not in updated


async def test_delete_user(client):
    """
    DELETE /users/{user_id} debe devolver 204 y luego el GET debe fallar (404 o 410).
    """
    created_res = await client.post("/users", json=sample_payload(email="del@test.com"))
    assert created_res.status_code == 201, created_res.text
    user_id = created_res.json()["id"]

    del_res = await client.delete(f"/users/{user_id}")
    assert del_res.status_code == 204, del_res.text

    get_res = await client.get(f"/users/{user_id}")
    assert get_res.status_code in (404, 410), get_res.text


# =========================
# Validaciones (422)
# =========================

async def test_create_user_missing_required_field_returns_422(client):
    """
    Si falta un campo requerido (ej: email), Pydantic debe responder 422.
    """
    payload = sample_payload()
    payload.pop("email")

    res = await client.post("/users", json=payload)
    assert res.status_code == 422, res.text


async def test_create_user_invalid_email_returns_422(client):
    """
    Si tu schema usa EmailStr para email, debe fallar con 422.
    (Si no usas EmailStr, este test fallará y lo ajustas o lo eliminas.)
    """
    res = await client.post("/users", json=sample_payload(email="not-an-email"))
    assert res.status_code == 422, res.text


async def test_update_user_invalid_email_returns_422(client):
    """
    PATCH con email inválido debería dar 422 si UserUpdate valida EmailStr.
    """
    created_res = await client.post("/users", json=sample_payload(email="valid@test.com"))
    assert created_res.status_code == 201, created_res.text
    user_id = created_res.json()["id"]

    res = await client.patch(f"/users/{user_id}", json={"email": "bad-email"})
    assert res.status_code == 422, res.text
