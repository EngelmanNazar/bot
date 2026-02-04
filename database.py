import sqlite3

connection = sqlite3.connect(
    "userdb.db",
    check_same_thread=False
)
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
    

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price INTEGER NOT NULL,
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
        print(f"✅ Пользователь добавлен: {user_id}")
        return True
    except Exception as e:
        print(f"❌ Ошибка при добавлении пользователя: {e}")
        return False

def get_all_users():
    try:
        cursor.execute("""
            SELECT user_id, username, first_name
            FROM users
            ORDER BY created_at DESC
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"❌ Ошибка при получении пользователей: {e}")
        return []

def add_product(name: str, description: str, price: int):
    try:
        cursor.execute("""
            INSERT INTO products (name, description, price)
            VALUES (?, ?, ?)
        """, (name, description, price))
        connection.commit()
        print(f"✅ Товар добавлен: {name}")
        return True
    except Exception as e:
        print(f"❌ Ошибка при добавлении товара: {e}")
        return False

def get_all_products():
    try:
        cursor.execute("""
            SELECT id, name, description, price
            FROM products
            ORDER BY created_at DESC
        """)
        return cursor.fetchall()
    except Exception as e:
        print(f"❌ Ошибка при получении товаров: {e}")
        return []