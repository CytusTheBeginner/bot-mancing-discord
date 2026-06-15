import mysql.connector
from mysql.connector import Error

# =========================
# DATABASE CONFIG
# =========================
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "fishing_bot",
    "autocommit": True
}

# =========================
# CONNECTION
# =========================
try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    print("[DB] Connected to MySQL")
except Error as e:
    raise RuntimeError(f"[DB] Connection failed: {e}")

# =========================
# INIT TABLES
# =========================
def init_db():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id BIGINT PRIMARY KEY,
        money INT DEFAULT 0,
        rod_level INT DEFAULT 1
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fish (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(50),
        chance FLOAT,
        image_url TEXT,
        price INT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        user_id BIGINT,
        fish_id INT,
        amount INT DEFAULT 1,
        PRIMARY KEY (user_id, fish_id)
    )
    """)

# =========================
# USER FUNCTIONS
# =========================
def get_user(user_id: int):
    cursor.execute(
        "SELECT * FROM users WHERE user_id = %s",
        (user_id,)
    )
    return cursor.fetchone()

def create_user(user_id: int):
    cursor.execute(
        "INSERT IGNORE INTO users (user_id) VALUES (%s)",
        (user_id,)
    )

def add_money(user_id: int, amount: int):
    cursor.execute(
        "UPDATE users SET money = money + %s WHERE user_id = %s",
        (amount, user_id)
    )

def get_money(user_id: int):
    cursor.execute(
        "SELECT money FROM users WHERE user_id = %s",
        (user_id,)
    )
    row = cursor.fetchone()
    return row["money"] if row else 0

# =========================
# FISH FUNCTIONS
# =========================
def get_fishes():
    cursor.execute("SELECT * FROM fish")
    return cursor.fetchall()

def get_fish_by_id(fish_id: int):
    cursor.execute(
        "SELECT * FROM fish WHERE id = %s",
        (fish_id,)
    )
    return cursor.fetchone()

# =========================
# INVENTORY FUNCTIONS
# =========================
def add_fish_to_inventory(user_id: int, fish_id: int):
    cursor.execute("""
        INSERT INTO inventory (user_id, fish_id, amount)
        VALUES (%s, %s, 1)
        ON DUPLICATE KEY UPDATE amount = amount + 1
    """, (user_id, fish_id))

def get_inventory(user_id: int):
    cursor.execute("""
        SELECT 
            fish.id,
            fish.name,
            fish.price,
            inventory.amount
        FROM inventory
        JOIN fish ON inventory.fish_id = fish.id
        WHERE inventory.user_id = %s
        ORDER BY fish.name
    """, (user_id,))
    return cursor.fetchall()

def get_fish_by_name(name: str):
    cursor.execute(
        "SELECT * FROM fish WHERE LOWER(name) = LOWER(%s)",
        (name,)
    )
    return cursor.fetchone()

def remove_fish(user_id: int, fish_id: int, amount: int = 1):
    cursor.execute("""
        UPDATE inventory
        SET amount = amount - %s
        WHERE user_id = %s AND fish_id = %s
    """, (amount, user_id, fish_id))

    cursor.execute("""
        DELETE FROM inventory
        WHERE amount <= 0
    """)

def get_inventory_by_rarity(user_id: int, rarity: str):
    cursor.execute("""
        SELECT
            fish.id,
            fish.price,
            inventory.amount
        FROM inventory
        JOIN fish ON inventory.fish_id = fish.id
        WHERE inventory.user_id = %s
        AND fish.rarity = %s
    """, (user_id, rarity))
    return cursor.fetchall()

def sell_by_rarity(user_id: int, rarity: str):
    items = get_inventory_by_rarity(user_id, rarity)

    if not items:
        return 0  # tidak ada yang dijual

    total_earned = 0

    conn.start_transaction()
    try:
        for item in items:
            subtotal = item["price"] * item["amount"]
            total_earned += subtotal

            cursor.execute("""
                DELETE FROM inventory
                WHERE user_id = %s AND fish_id = %s
            """, (user_id, item["id"]))

        cursor.execute("""
            UPDATE users
            SET money = money + %s
            WHERE user_id = %s
        """, (total_earned, user_id))

        conn.commit()
        return total_earned

    except Exception:
        conn.rollback()
        raise

def get_user_profile(user_id: int):
    cursor.execute("""
        SELECT
            u.user_id,
            u.money,
            u.rod_level,
            COALESCE(SUM(i.amount), 0) AS total_fish,
            COALESCE(SUM(i.amount * f.price), 0) AS inventory_value
        FROM users u
        LEFT JOIN inventory i ON u.user_id = i.user_id
        LEFT JOIN fish f ON i.fish_id = f.id
        WHERE u.user_id = %s
        GROUP BY u.user_id
    """, (user_id,))
    return cursor.fetchone()

# =========================
# TRANSACTION HELPERS
# =========================
def begin():
    conn.start_transaction()

def commit():
    conn.commit()

def rollback():
    conn.rollback()

# =========================
# OPTIONAL: SAFE SHUTDOWN
# =========================
def close_db():
    cursor.close()
    conn.close()
    print("[DB] Connection closed")
