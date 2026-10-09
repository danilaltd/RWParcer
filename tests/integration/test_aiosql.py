from typing import TYPE_CHECKING, Protocol, TypedDict, cast

import aiosql
import asyncpg
import pytest
from testcontainers.community.postgres import PostgresContainer

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


class UserRow(TypedDict):
    id: int
    name: str


class UserQueries(Protocol):
    def get_users(
        self,
        conn: asyncpg.Connection,
    ) -> AsyncIterator[UserRow]: ...

    async def get_user_by_id(
        self,
        conn: asyncpg.Connection,
        *,
        id: int,
    ) -> UserRow | None: ...

    async def user_exists(
        self,
        conn: asyncpg.Connection,
        *,
        id: int,
    ) -> bool: ...

    async def insert_user(
        self,
        conn: asyncpg.Connection,
        *,
        id: int,
        name: str,
    ) -> None: ...

    async def update_user(
        self,
        conn: asyncpg.Connection,
        *,
        id: int,
        name: str,
    ) -> None: ...

    async def delete_user(
        self,
        conn: asyncpg.Connection,
        *,
        id: int,
    ) -> None: ...


def _load_queries[QueriesT](sql_text: str) -> QueriesT:
    return cast(
        "QueriesT",
        aiosql.from_str(sql_text, driver_adapter="asyncpg"),
    )


@pytest.mark.asyncio
async def test_aiosql_asyncpg_modifiers() -> None:
    with PostgresContainer("postgres:16-alpine") as postgres:
        conn = await asyncpg.connect(postgres.get_connection_url(driver=None))

        try:
            queries: UserQueries = _load_queries(
                """
                -- name: get_users()
                SELECT id, name
                FROM test_users
                ORDER BY id;

                -- name: get_user_by_id(id)^
                SELECT id, name
                FROM test_users
                WHERE id = :id;

                -- name: user_exists(id)$
                SELECT EXISTS(
                    SELECT 1
                    FROM test_users
                    WHERE id = :id
                );

                -- name: insert_user(id, name)!
                INSERT INTO test_users (id, name)
                VALUES (:id, :name);

                -- name: update_user(id, name)!
                UPDATE test_users
                SET name = :name
                WHERE id = :id;

                -- name: delete_user(id)!
                DELETE FROM test_users
                WHERE id = :id;
                """,
            )
            await conn.execute(
                """
                CREATE TABLE test_users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                )
                """
            )

            await queries.insert_user(conn, id=1, name="Alice")
            await queries.insert_user(conn, id=2, name="Bob")

            user = await queries.get_user_by_id(conn, id=1)

            assert user is not None
            assert user["id"] == 1
            assert user["name"] == "Alice"

            assert await queries.user_exists(conn, id=1) is True
            assert await queries.user_exists(conn, id=999) is False

            users = [row async for row in queries.get_users(conn)]

            assert len(users) == 2
            assert [user["name"] for user in users] == [
                "Alice",
                "Bob",
            ]

            await queries.update_user(
                conn,
                id=1,
                name="Alice Updated",
            )

            user = await queries.get_user_by_id(conn, id=1)

            assert user is not None
            assert user["name"] == "Alice Updated"

            await queries.delete_user(conn, id=1)

            assert await queries.user_exists(conn, id=1) is False

        finally:
            await conn.close()
