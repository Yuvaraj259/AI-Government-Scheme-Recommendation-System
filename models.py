from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection

class User(UserMixin):
    def __init__(self, user_id, name, email, role, password_hash):
        self.id = user_id
        self.name = name
        self.email = email
        self.role = role
        self.password_hash = password_hash

    @staticmethod
    def get(user_id):
        conn = get_db_connection()
        if not conn:
            return None
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user_data:
            return User(
                user_id=user_data['user_id'],
                name=user_data['name'],
                email=user_data['email'],
                role=user_data['role'],
                password_hash=user_data['password_hash']
            )
        return None

    @staticmethod
    def get_by_email(email):
        conn = get_db_connection()
        if not conn:
            return None
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user_data:
            return User(
                user_id=user_data['user_id'],
                name=user_data['name'],
                email=user_data['email'],
                role=user_data['role'],
                password_hash=user_data['password_hash']
            )
        return None

    @staticmethod
    def create(name, email, password, role='user'):
        hashed_password = generate_password_hash(password)
        conn = get_db_connection()
        if not conn:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                (name, email, hashed_password, role)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
