from db import get_db_connection
import json
import decimal
import datetime

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super().default(obj)

def dump_db():
    conn = get_db_connection()
    if not conn:
        print("Connection failed")
        return

    cursor = conn.cursor(dictionary=True)
    
    # Get schemes
    cursor.execute("SELECT * FROM schemes")
    schemes = cursor.fetchall()
    
    # Get rules
    cursor.execute("SELECT * FROM eligibility_rules")
    rules = cursor.fetchall()
    
    data = {
        "schemes": schemes,
        "rules": rules
    }
    
    print(f"Found {len(schemes)} schemes and {len(rules)} rules.")
    
    with open('db_dump_utf8.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, cls=CustomEncoder, indent=2)

if __name__ == "__main__":
    dump_db()
