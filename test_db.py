import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

try:
    database_url = os.getenv("DATABASE_URL")

    conn = psycopg2.connect(database_url)

    print("Database connected successfully!")

    cursor = conn.cursor()

    cursor.execute("SELECT version();")

    print("PostgreSQL Version:")
    print(cursor.fetchone()[0])

    cursor.close()
    conn.close()

    print("Connection closed successfully!")

except Exception as e:
    print("Database connection failed!")
    print("Error:", e)