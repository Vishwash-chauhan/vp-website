import pymysql

try:
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='vyapaarniti_db',
        charset='utf8mb4'
    )
    print("✅ MySQL connection successful!")
    
    with connection.cursor() as cursor:
        cursor.execute("DESCRIBE experts")
        columns = cursor.fetchall()
        print(f"Current experts table columns: {len(columns)}")
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
    
    connection.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
