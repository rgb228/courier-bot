import aiosqlite
import os

# Путь к базе данных внутри папки data
DB_PATH = "data/leads.db"

# Автоматически создаем папку data, если ее нет (для Render)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                phone TEXT,
                status TEXT DEFAULT 'new',
                date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        try:
            await db.execute("ALTER TABLE users ADD COLUMN phone TEXT")
        except aiosqlite.OperationalError:
            pass # Колонка уже существует
        await db.commit()

async def save_user(user_id, username, first_name):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
            (user_id, username, first_name)
        )
        await db.commit()

async def save_phone(user_id, phone):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET phone = ? WHERE user_id = ?", (phone, user_id))
        await db.commit()

async def update_status(user_id, status):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET status = ? WHERE user_id = ?", (status, user_id))
        await db.commit()

async def get_users(status=None):
    async with aiosqlite.connect(DB_PATH) as db:
        if status:
            cursor = await db.execute("SELECT user_id, username, first_name, phone, status FROM users WHERE status = ?", (status,))
        else:
            cursor = await db.execute("SELECT user_id, username, first_name, phone, status FROM users")
        return await cursor.fetchall()

async def get_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        total = (await cursor.fetchone())[0]
        cursor = await db.execute("SELECT COUNT(*) FROM users WHERE status = 'registered'")
        registered = (await cursor.fetchone())[0]
        return total, registered