from db import get_db_connection
import mysql.connector

def test_connection():
    print("Testing Database Connection...")
    conn = get_db_connection()
    if conn:
        print("✅ Connection Successful!")
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT count(*) as count FROM schemes")
        result = cursor.fetchone()
        print(f"✅ Found {result['count']} schemes in the database.")
        
        cursor.execute("SELECT * FROM schemes LIMIT 1")
        scheme = cursor.fetchone()
        print("Sample Scheme:", scheme)
        
        conn.close()
    else:
        print("❌ Connection Failed.")
        # Try to print more details by manually connecting without the helper to catch the exception explicitly if helper suppressed it (though helper currently prints it)
        try:
            import os
            from dotenv import load_dotenv
            load_dotenv()
            print(f"Attempting connect with: Host={os.getenv('DB_HOST')}, User={os.getenv('DB_USER')}, DB={os.getenv('DB_NAME')}")
            # we don't print password for security in logs, but we know it's from env
            
            mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", ""),
                database=os.getenv("DB_NAME", "gov_schemes_db")
            )
        except Exception as e:
            print(f"❌ Detailed Error: {e}")

if __name__ == "__main__":
    test_connection()
