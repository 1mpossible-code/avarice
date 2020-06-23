import sqlite3
import logging

# Initializing logs
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

log.debug("Trying to connect to database.sqlite or create new if not exist")
conn = sqlite3.connect("database.sqlite", check_same_thread=False)

with conn:
    log.debug("Initializing cursor")
    cursor = conn.cursor()

    # Creating user table if not exists
    cursor.executescript("""CREATE TABLE IF NOT EXISTS users
        (
             chat_id INTEGER not null
                primary key,
            first_name VARCHAR not null,
            username VARCHAR,
            phone_number VARCHAR,
            cart TEXT,
            is_operator BOOLEAN,
            is_administrator BOOLEAN
        );
        """)

    # Creating category table if not exists
    cursor.executescript("""CREATE TABLE IF NOT EXISTS categories
        (
             category_id INTEGER not null
                primary key autoincrement,
            title VARCHAR
        );
        """)

    # Creating products table if not exists
    cursor.executescript("""CREATE TABLE IF NOT EXISTS products
        (
             id INTEGER not null
                primary key autoincrement,
            title VARCHAR,
            description TEXT,
            price INTEGER,
            image BLOB,
            category_id INTEGER,
            bot_shows BOOLEAN
        );
        """)

    # Creating orders table if not exists
    cursor.executescript("""CREATE TABLE IF NOT EXISTS orders
        (
             order_id INTEGER not null
                primary key autoincrement,
            chat_id INTEGER,
            user_full_name TEXT,
            total_price INTEGER,
            order_date DATE,
            status INTEGER,
            note TEXT
        );
        """)
    conn.commit()


def if_user_exists(chat_id):
    try:
        cursor.execute("SELECT * FROM users WHERE chat_id LIKE ?", [chat_id])
        g_user = cursor.fetchall()
        log.debug(g_user[0][1] + " was checked on existing")
        return True
    except IndexError:
        return False


def new_user(chat_id, first_name, username, phone_number):
    cursor.execute("""INSERT INTO users (chat_id, first_name, username, phone_number, is_operator, is_administrator) 
    VALUES (?, ?, ?, ?, ?, ?)
    """, (chat_id, first_name, username, phone_number, None, None))
    conn.commit()


def new_order(chat_id, user_full_name, total_price, order_date, status, note):
    cursor.execute("""
    INSERT INTO orders (chat_id, user_full_name, total_price, order_date, status, note) VALUES (?, ?, ?, ?, ?, ?)
    """, (chat_id, user_full_name, total_price, order_date, status, note))
    conn.commit()


def add_category(title):
    cursor.execute("INSERT INTO category (title) VALUES (?)",
                   [title])
    conn.commit()
    log.debug(f"Added category: {title}")


def add_product(title, description, price, image, category_id):
    cursor.execute("""INSERT INTO products (title, description, price, image, category_id, bot_shows) 
    VALUES (?, ?, ?, ?, ?, ?)""", (title, description, price, image, category_id, 1))
    conn.commit()


def get_categories():
    cursor.execute("SELECT * FROM categories")
    return cursor.fetchall()


def get_products():
    cursor.execute("SELECT * FROM products")
    return cursor.fetchall()


def get_product_ids():
    cursor.execute("SELECT id FROM products")
    return cursor.fetchall()


def get_product_by_id(prod_id):
    cursor.execute("SELECT * FROM products WHERE id LIKE ?", [prod_id])
    product = cursor.fetchall()
    return product[0]


def get_user_by_id(user_id):
    cursor.execute("SELECT * FROM users WHERE chat_id LIKE ?", [user_id])
    g_user = cursor.fetchall()
    try:
        return g_user[0]
    except IndexError:
        return None


def search_product(search_text):
    cursor.execute("SELECT * FROM products WHERE title LIKE ?", [search_text])
    log.debug(f"Search: {search_text}")
    products = cursor.fetchall()
    return products


# add_product("cat", "this is good cat item", 300, "images/item_1.png", 12)
# new_user("778508362", "Max", None, "+38095")
# pr = get_products()
# print(get_products())
