import asyncpg
import os
import asyncio

# Render передает строку подключения в переменную DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Функция для получения пула соединений
async def get_pool():
    return await asyncpg.create_pool(DATABASE_URL)

async def init_db():
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                phone TEXT,
                status TEXT DEFAULT 'new',
                date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    await pool.close()

async def save_user(user_id, username, first_name):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO users (user_id, username, first_name) VALUES (, , ) ON CONFLICT (user_id) DO NOTHING",
            user_id, username, first_name
        )
    await pool.close()

async def save_phone(user_id, phone):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE users SET phone =  WHERE user_id = ", phone, user_id)
    await pool.close()

async def update_status(user_id, status):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("UPDATE users SET status =  WHERE user_id = ", status, user_id)
    await pool.close()

async def get_users(status=None):
    pool = await get_pool()
    async with pool.acquire() as conn:
        if status:
            rows = await conn.fetch("SELECT user_id, username, first_name, phone, status FROM users WHERE status = ", status)
        else:
            rows = await conn.fetch("SELECT user_id, username, first_name, phone, status FROM users")
    await pool.close()
    return [tuple(row) for row in rows]

async def get_stats():
    pool = await get_pool()
    async with pool.acquire() as conn:
        total = await conn.fetchval("SELECT COUNT(*) FROM users")
        registered = await conn.fetchval("SELECT COUNT(*) FROM users WHERE status = 'registered'")
    await pool.close()
    return total, registered