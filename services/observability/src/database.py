import os
from typing import AsyncGenerator
import psycopg
# type: ignore
from psycopg_pool import AsyncConnectionPool

def get_db_url() -> str:
    user = os.getenv("POSTGRES_USER", "scof")
    pw = os.getenv("POSTGRES_PASSWORD", "changeme")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "scof")
    return f"postgresql://{user}:{pw}@{host}:{port}/{db}"

pool: AsyncConnectionPool | None = None

async def init_db_pool():
    global pool
    pool = AsyncConnectionPool(get_db_url(), min_size=1, max_size=10)
    await pool.open()

async def close_db_pool():
    global pool
    if pool:
        await pool.close()
        pool = None

async def get_db() -> AsyncGenerator[psycopg.AsyncConnection, None]:
    if pool is None:
        raise RuntimeError("Database pool not initialized")
    async with pool.connection() as conn:
        yield conn
