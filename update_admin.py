from db import get_db_connection
from werkzeug.security import generate_password_hash
import mysql.connector

def update_admin():
    conn = get_db_connection()
    if not conn:
        print("Database connection failed.")
        return

    try:
        cursor = conn.cursor()
        
        email = "admin@gmail.com"
        password = "admin123@#"
        hashed_pw = generate_password_hash(password)

        # Check if this specific admin email exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            # Update password
            print(f"Updating password for {email}...")
            cursor.execute("UPDATE users SET password_hash = %s, role = 'admin' WHERE email = %s", (hashed_pw, email))
        else:
            # Check if OLD admin exists (admin@gov.in) and update it, OR create new
            cursor.execute("SELECT * FROM users WHERE role = 'admin' LIMIT 1")
            existing_admin = cursor.fetchone()
            
            if existing_admin:
                print(f"Updating existing admin ({existing_admin[2]}) to new credentials...")
                cursor.execute("UPDATE users SET email = %s, password_hash = %s WHERE user_id = %s", (email, hashed_pw, existing_admin[0]))
            else:
                print(f"Creating new admin {email}...")
                cursor.execute("INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, 'admin')", ("Super Admin", email, hashed_pw))
        
        conn.commit()
        print(f"Admin access restricted to: {email}")
        print(f"Password updated to: {password}")
        
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    update_admin()
