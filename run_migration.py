
from config import Config
from sqlalchemy import create_engine, text

# Connect to PostgreSQL
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

try:
    with engine.begin() as connection:

        connection.execute(text("""
            ALTER TABLE crops
            ADD COLUMN IF NOT EXISTS variety VARCHAR(255);
        """))

    print("Migration completed successfully!")
    print("Variety column added to crops table.")

except Exception as e:
    print("Migration failed:", e)
