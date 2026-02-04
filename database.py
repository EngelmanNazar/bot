import sqlite3

connection = sqlite3.connect("userdb.db", check_same_thread=False)
cursor = connection.cursor()

def init_db():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            username TEXT,
            first_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    connection.commit()
    print("✅ База данных инициализирована")

def add_user(user_id: int, username: str, first_name: str):
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
        """, (user_id, username, first_name))
        connection.commit()
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def get_all_users():
    try:
        cursor.execute("SELECT user_id, username, first_name FROM users ORDER BY created_at DESC")
        return cursor.fetchall()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return []