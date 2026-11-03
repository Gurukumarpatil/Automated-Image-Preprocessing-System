from db import get_db_connection

try:
    connection = get_db_connection()

    with connection.cursor() as cursor:
        cursor.execute("SELECT DATABASE() AS database_name")
        result = cursor.fetchone()
        print("Connected to AWS RDS successfully!")
        print("Database:", result["database_name"])

        cursor.execute("SHOW TABLES")
        print("Tables:", cursor.fetchall())

    connection.close()

except Exception as error:
    print("Database connection failed:", error)