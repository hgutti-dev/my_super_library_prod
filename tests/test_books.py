# tests/test_books.py
import pytest

""" 
Importa pytest.

pytestmark = pytest.mark.anyio aplica el mark a todos los tests del archivo, para que pytest sepa que se ejecutan en modo async (con AnyIO).
Eso permite que tus funciones async def test_...() corran bien.
"""
pytestmark = pytest.mark.anyio


"""  
Esto es un helper para no repetir JSON en cada test:

Define un payload base válido para crear un libro (BookCreate).

Te deja “sobrescribir” campos con overrides, ejemplo:

sample_payload(title="Book X")

sample_payload(total_copies=-1)

Así tus tests quedan limpios y consistentes.
"""
def sample_payload(**overrides):
    """
    Payload base EXACTO para BookCreate (según src/schemas/book.py).
    """
    payload = {
        "title": "Clean Architecture",
        "author": "Robert C. Martin",
        "genre": "Software",
        "total_copies": 5,
    }
    payload.update(overrides)
    return payload


async def test_list_books_empty(client):
    res = await client.get("/books")
    assert res.status_code == 200
    assert res.json() == []


async def test_create_book_returns_bookread(client):
    res = await client.post("/books", json=sample_payload())
    assert res.status_code == 201, res.text

    data = res.json()

    # BookRead: id + campos base
    assert "id" in data and isinstance(data["id"], str) and data["id"]
    assert data["title"] == "Clean Architecture"
    assert data["author"] == "Robert C. Martin"
    assert data["genre"] == "Software"
    assert data["total_copies"] == 5


async def test_get_book_by_id(client):
    created_res = await client.post("/books", json=sample_payload(title="Book X"))
    assert created_res.status_code == 201, created_res.text
    created = created_res.json()
    book_id = created["id"]

    res = await client.get(f"/books/{book_id}")
    assert res.status_code == 200, res.text
    got = res.json()

    assert got["id"] == book_id
    assert got["title"] == "Book X"
    assert got["author"] == "Robert C. Martin"
    assert got["genre"] == "Software"
    assert got["total_copies"] == 5


async def test_list_books_with_filters(client):
    await client.post("/books", json=sample_payload(title="Book A", author="Author 1", genre="Fantasy", total_copies=1))
    await client.post("/books", json=sample_payload(title="Book B", author="Author 2", genre="Sci-Fi", total_copies=2))

    # title exacto
    r1 = await client.get("/books", params={"title": "Book A"})
    assert r1.status_code == 200, r1.text
    d1 = r1.json()
    assert len(d1) == 1
    assert d1[0]["title"] == "Book A"

    # author exacto
    r2 = await client.get("/books", params={"author": "Author 2"})
    assert r2.status_code == 200, r2.text
    d2 = r2.json()
    assert len(d2) == 1
    assert d2[0]["author"] == "Author 2"

    # genre exacto
    r3 = await client.get("/books", params={"genre": "Fantasy"})
    assert r3.status_code == 200, r3.text
    d3 = r3.json()
    assert len(d3) == 1
    assert d3[0]["genre"] == "Fantasy"


async def test_update_book_patch(client):
    created_res = await client.post("/books", json=sample_payload(title="Old Title", total_copies=3))
    assert created_res.status_code == 201, created_res.text
    book_id = created_res.json()["id"]

    # BookUpdate permite campos opcionales
    patch_res = await client.patch(f"/books/{book_id}", json={"title": "New Title", "total_copies": 10})
    assert patch_res.status_code == 200, patch_res.text
    updated = patch_res.json()

    assert updated["id"] == book_id
    assert updated["title"] == "New Title"
    assert updated["total_copies"] == 10


async def test_delete_book(client):
    created_res = await client.post("/books", json=sample_payload(title="To Delete"))
    assert created_res.status_code == 201, created_res.text
    book_id = created_res.json()["id"]

    del_res = await client.delete(f"/books/{book_id}")
    assert del_res.status_code == 204

    # Luego debería ser 404 (lo común). Si tu service usa otro código, aquí lo ajustamos.
    get_res = await client.get(f"/books/{book_id}")
    assert get_res.status_code in (404, 410)


async def test_create_book_total_copies_negative_returns_422(client):
    res = await client.post("/books", json=sample_payload(total_copies=-1))
    assert res.status_code == 422


async def test_update_book_total_copies_negative_returns_422(client):
    created_res = await client.post("/books", json=sample_payload(total_copies=1))
    assert created_res.status_code == 201, created_res.text
    book_id = created_res.json()["id"]

    # En update, total_copies < 0 también debe disparar 422 por validación Pydantic
    patch_res = await client.patch(f"/books/{book_id}", json={"total_copies": -5})
    assert patch_res.status_code == 422
