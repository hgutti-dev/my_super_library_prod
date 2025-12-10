# src/utils/test_book_repo.py

import asyncio
from datetime import date

from motor.motor_asyncio import AsyncIOMotorClient

from src.repositories.book_repository import BookRepository
from src.schemas.book import BookCreate, BookUpdate


# Ajusta estos valores a tu entorno
MONGO_URI = "mongodb+srv://hert_guti91:CD3PB8p1ozv6fSoV@myclostercafe.i54yopc.mongodb.net/"
DB_NAME = "demo_db"


async def main():
    # 1. Conectar a Mongo
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]

    repo = BookRepository(db)

    # ============ 1) CREATE ============
    nuevo_libro = BookCreate(
        title="Clean Code",
        author="Robert C. Martin",
        genre="Software",
        total_copies=15,
    )

    creado = await repo.create_book(nuevo_libro)
    print("CREATED:", creado)

    creado = "6939baae9689a8b88e1dc261"

    # ============ 2) GET BY ID ============
    libro = await repo.get_book_by_id(creado)
    print("GET BY ID:", libro)

    # ============ 3) LIST ============
    libros = await repo.list_books(skip=0, limit=10)
    print("LIST BOOKS (count):", len(libros))
    for b in libros:
        print("-", b.id, b.title, b.genre)

    # ============ 4) UPDATE ============

    creado = "6939baae9689a8b88e1dc261"

    update_data = BookUpdate(
        title="Clean Code (3nd Edition)",
        total_copies=10,
    )
    actualizado = await repo.update_book(creado, update_data)
    print("UPDATED:", actualizado)

    # ============ 5) DELETE ============
    borrado = await repo.delete_book(creado)
    print("DELETED:", borrado)

    client.close()


if __name__ == "__main__":
    asyncio.run(main())
