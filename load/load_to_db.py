import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import URL

# Load variables from .env file
load_dotenv()


def get_db_engine():
    """Build and return the SQLAlchemy engine from environment variables."""
    db_url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 5432)),
        database=os.getenv("DB_NAME"),
    )

    return create_engine(db_url)


def load(df):
    engine = get_db_engine()

    # Test connection before attempting load
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        print("✅ Database connection successful.")

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise

    inspector = inspect(engine)
    table_exists = inspector.has_table("countries")

    if table_exists:
        print("  Existing 'countries' table found.")
        print("  Clearing old records without dropping the table...")

        with engine.begin() as conn:
            conn.execute(text("TRUNCATE TABLE countries"))

        df.to_sql(
            name="countries",
            con=engine,
            if_exists="append",
            index=False,
        )

    else:
        print("  'countries' table does not exist. Creating table...")

        df.to_sql(
            name="countries",
            con=engine,
            if_exists="append",
            index=False,
        )

    print(f"✅ Loaded {len(df)} rows into 'countries' table.")
