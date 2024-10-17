import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from passlib.context import CryptContext

DATABASE_NAME = 'users.db'
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def register_user(email, password):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    hashed_password =  pwd_context.hash(password)#generate_password_hash(password)
    try:
        cursor.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, hashed_password))
        conn.commit()
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()
    return True

def login_user(email, password):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user and pwd_context.verify(password, user[0]): #check_password_hash(user[0], password):
        return True
    return False
