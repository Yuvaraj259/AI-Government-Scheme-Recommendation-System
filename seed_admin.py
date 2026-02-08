from db import get_db_connection
from werkzeug.security import generate_password_hash
import mysql.connector

def create_admin():
    conn = get_db_connection()
    if not conn:
        print("❌ Database connection failed.")
        return

    try:
        cursor = conn.cursor()
        
        # Check if admin exists
        cursor.execute("SELECT * FROM users WHERE email = 'admin@gov.in'")
        if cursor.fetchone():
            print("ℹ️ Admin account already exists (admin@gov.in).")
            return

        # Create Admin
        password = "admin123"
        hashed_pw = generate_password_hash(password)
        
        query = "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, ("Super Admin", "admin@gov.in", hashed_pw, "admin"))
        conn.commit()
        
        print("✅ Admin account created successfully!")
        print("Email: admin@gov.in")
        print("Password: " + password)
        
    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_admin()
