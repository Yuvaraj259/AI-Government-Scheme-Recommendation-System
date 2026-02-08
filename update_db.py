from db import get_db_connection
import mysql.connector

def apply_schema_update():
    print("Updating Database Schema...")
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Create Users Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                role ENUM('user', 'admin') DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            conn.commit()
            print("✅ Users table created successfully.")
        except mysql.connector.Error as err:
            print(f"❌ Error: {err}")
        finally:
            cursor.close()
            conn.close()
    else:
        print("❌ Connection Failed.")

if __name__ == "__main__":
    apply_schema_update()
