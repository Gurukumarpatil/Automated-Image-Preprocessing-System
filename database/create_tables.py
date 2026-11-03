import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

connection = pymysql.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    connect_timeout=10
)

try:
    with connection.cursor() as cursor:
        with open("database/schema.sql", "r") as file:
            sql_commands = file.read().split(";")

        for command in sql_commands:
            if command.strip():
                cursor.execute(command)

    connection.commit()
    print("Database and tables created successfully!")

finally:
    connection.close()